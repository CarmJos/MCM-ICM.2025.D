# model.py
from dataclasses import dataclass

import numpy as np
import pandas as pd
import networkx as nx
from typing import List, Dict

from data.dataset import Dataset, Node, Edge
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor


def compute_betweenness(graph, nodes_chunk, weight=None):
    # 计算指定节点集的介数中心性
    return nx.betweenness_centrality(graph, nodes_chunk, weight=weight)


def parallel_betweenness_centrality_with_progress(graph, weight='weight', num_threads=8):
    nodes = list(graph.nodes)
    chunk_size = len(nodes) // num_threads
    node_chunks = [nodes[i:i + chunk_size] for i in range(0, len(nodes), chunk_size)]

    # 创建一个线程池，使用进度条显示进度
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(tqdm(executor.map(lambda chunk: compute_betweenness(graph, chunk, weight), node_chunks),
                            total=len(node_chunks)))

    # 合并所有线程计算的结果
    betweenness = {}
    for result in results:
        betweenness.update(result)

    return betweenness


class NetworkEvaluator:
    """交通网络节点重要度评估模型"""

    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.graph = self._build_networkx_graph()
        self.metrics = {
            'degree_centrality': {},
            'betweenness_centrality': {},
            'closeness_centrality': {},
            'eigenvector_centrality': {},
            'pagerank': {},
            'connection_strength': {}
        }

    def _build_networkx_graph(self) -> nx.Graph:
        """将数据集转换为networkx图结构（带进度条）"""
        g = nx.Graph()
        for node in tqdm(self.dataset.nodes, desc="BUILDING NODES"):
            g.add_node(node.id, data=node)
        for edge in tqdm(self.dataset.edges, desc="BUILDING EDGES"):
            g.add_edge(edge.u, edge.v, weight=edge.length)
        return g

    def calculate_degree_centrality(self):
        """度中心性计算"""
        print("Calculating degree centrality...")
        self.metrics['degree_centrality'] = nx.degree_centrality(self.graph)

    def calculate_betweenness_centrality(self):
        """介数中心性计算"""
        print("Calculating betweenness centrality...")
        self.metrics['betweenness_centrality'] = nx.betweenness_centrality(self.graph, weight='weight')
        # self.metrics['betweenness_centrality'] = parallel_betweenness_centrality_with_progress(self.graph)

    def calculate_closeness_centrality(self):
        """紧密中心性计算"""
        print("Calculating closeness centrality...")
        self.metrics['closeness_centrality'] = nx.closeness_centrality(self.graph, distance='weight')

    def calculate_eigenvector_centrality(self):
        """特征向量中心性计算"""
        print("Calculating eigenvector centrality...")
        try:
            self.metrics['eigenvector_centrality'] = nx.eigenvector_centrality(self.graph, max_iter=1000)
        except nx.PowerIterationFailedConvergence:
            print("特征向量中心性计算未收敛，使用默认值")
            self.metrics['eigenvector_centrality'] = {n: 0 for n in self.graph.nodes}

    def calculate_pagerank(self):
        """PageRank值计算"""
        print("Calculating PageRank...")
        self.metrics['pagerank'] = nx.pagerank(self.graph, alpha=0.85)

    def calculate_connection_strength(self):
        """连接强度计算（带进度条）"""
        connection_strength = {node.id: 0 for node in self.dataset.nodes}

        print("Calculating connection strength...")
        for traffic in tqdm(self.dataset.traffic):
            if traffic.aadt_motorcycle and traffic.aadt_bus:
                total_flow = (traffic.aadt_motorcycle + traffic.aadt_bus) or 1

                # 处理起始节点
                for nid in traffic.node_start:
                    if node := self.dataset.node(nid):
                        connection_strength[node.id] += total_flow / len(traffic.node_start)

                # 处理结束节点
                for nid in traffic.node_end:
                    if node := self.dataset.node(nid):
                        connection_strength[node.id] += total_flow / len(traffic.node_end)

        self.metrics['connection_strength'] = connection_strength

    def normalize_metrics(self) -> pd.DataFrame:
        """指标归一化处理"""
        df = pd.DataFrame(self.metrics)

        # 最大最小值归一化
        for col in df.columns:
            if col != 'connection_strength':
                df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

        # 连接强度特殊处理（对数变换）
        df['connection_strength'] = np.log1p(df['connection_strength'])
        df['connection_strength'] = df['connection_strength'] / df['connection_strength'].max()

        return df.fillna(0)

    def cosine_topsis(self, weights: Dict[str, float] = None) -> pd.Series:
        """
        基于余弦相似性的TOPSIS评估
        :param weights: 各指标权重，默认等权
        """
        df = self.normalize_metrics()

        # 设置默认权重
        if not weights:
            weights = {col: 1 / len(df.columns) for col in df.columns}

        # 加权处理
        weighted_matrix = df * pd.Series(weights)

        # 计算理想解
        ideal_best = weighted_matrix.max()
        ideal_worst = weighted_matrix.min()

        # 余弦相似度计算
        def cosine_sim(row, ideal):
            return np.dot(row, ideal) / (np.linalg.norm(row) * np.linalg.norm(ideal))

        sim_best = weighted_matrix.apply(lambda row: cosine_sim(row, ideal_best), axis=1)
        sim_worst = weighted_matrix.apply(lambda row: cosine_sim(row, ideal_worst), axis=1)

        # 计算贴近度
        closeness = sim_best / (sim_best + sim_worst)
        return closeness.sort_values(ascending=False)

    def full_evaluation(self, weights: Dict[str, float] = None) -> pd.DataFrame:

        self.calculate_degree_centrality()
        self.calculate_betweenness_centrality()
        self.calculate_closeness_centrality()
        self.calculate_eigenvector_centrality()
        self.calculate_pagerank()
        self.calculate_connection_strength()

        # TOPSIS评估
        print("Performing TOPSIS evaluation...")
        topsis_result = self.cosine_topsis(weights)

        # 结果整合
        result_df = pd.DataFrame({
            'node_id': topsis_result.index,
            'importance_score': topsis_result.values,
            **self.metrics
        })

        return result_df.sort_values('importance_score', ascending=False)
