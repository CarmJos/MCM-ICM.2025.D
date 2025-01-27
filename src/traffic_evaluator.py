from collections.abc import Callable
from typing import Dict

import networkit as nk
import numpy as np
import pandas as pd
from tqdm import tqdm

from data.dataset import Dataset, Traffic


class NetworkEvaluator:

    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.graph = self._build_networkit_graph()
        self.metrics = {
            'degree_centrality': {},
            'betweenness_centrality': {},
            'closeness_centrality': {},
            'eigenvector_centrality': {},
            'pagerank': {}
        }

    def _build_networkit_graph(self) -> nk.Graph:
        g = nk.Graph(len(self.dataset.nodes), directed=False)
        node_mapping = {node.id: i for i, node in enumerate(self.dataset.nodes)}

        for edge in tqdm(self.dataset.edges, desc="BUILDING EDGES"):
            u = node_mapping[edge.u]
            v = node_mapping[edge.v]
            if edge.oneway:
                if edge.reversed:
                    g.addEdge(v, u)  # 从v到u
                else:
                    g.addEdge(u, v)  # 从u到v
            else:
                # 双向边
                g.addEdge(u, v)
                g.addEdge(v, u)

        return g

    def calculate_degree_centrality(self):
        print("Calculating degree centrality...")
        deg_centrality = nk.centrality.DegreeCentrality(self.graph)
        deg_centrality.run()
        self.metrics['degree_centrality'] = {node.id: deg_centrality.score(i) for i, node in
                                             enumerate(self.dataset.nodes)}

    def calculate_betweenness_centrality(self):
        print("Calculating betweenness centrality...")
        bet_centrality = nk.centrality.Betweenness(self.graph, normalized=True)
        bet_centrality.run()
        self.metrics['betweenness_centrality'] = {node.id: bet_centrality.score(i) for i, node in
                                                  enumerate(self.dataset.nodes)}

    def calculate_closeness_centrality(self):
        print("Calculating closeness centrality...")
        closeness_centrality = nk.centrality.Closeness(self.graph, True, True)
        closeness_centrality.run()
        self.metrics['closeness_centrality'] = {node.id: closeness_centrality.score(i) for i, node in
                                                enumerate(self.dataset.nodes)}

    def calculate_eigenvector_centrality(self):
        print("Calculating eigenvector centrality...")
        try:
            eigen_centrality = nk.centrality.EigenvectorCentrality(self.graph)
            eigen_centrality.run()
            self.metrics['eigenvector_centrality'] = {node.id: eigen_centrality.score(i) for i, node in
                                                      enumerate(self.dataset.nodes)}
        except Exception as e:
            print(f"特征向量中心性计算出错: {e}")
            self.metrics['eigenvector_centrality'] = {n: 0 for n in self.dataset.nodes}

    def calculate_pagerank(self):
        print("Calculating PageRank...")
        pagerank = nk.centrality.PageRank(self.graph, damp=0.85)
        pagerank.run()
        self.metrics['pagerank'] = {node.id: pagerank.score(i) for i, node in enumerate(self.dataset.nodes)}

    def cosine_topsis(self, weights: Dict[str, float] = None) -> pd.Series:
        """
        基于余弦相似性的TOPSIS评估
        :param weights: 各指标权重，默认等权
        """
        df = pd.DataFrame(self.metrics)

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
            norm_row = np.linalg.norm(row)
            norm_ideal = np.linalg.norm(ideal)
            if norm_row == 0 or norm_ideal == 0:
                return 0  # 如果任一向量为零向量，返回相似度为 0
            return np.dot(row, ideal) / (norm_row * norm_ideal)

        # 计算相似度
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

        print("Performing TOPSIS evaluation...")
        topsis_result = self.cosine_topsis(weights)

        # 将 self.metrics 中的字典转换为 pandas.Series
        metrics_series = {k: pd.Series(v) for k, v in self.metrics.items()}

        # 结果整合
        result_df = pd.DataFrame({
            'node': topsis_result.index,
            'score': topsis_result.values,
            **metrics_series  # 展开转换后的 metrics_series
        })

        return result_df.sort_values('score', ascending=False)


def evaluate(dataset: Dataset) -> pd.DataFrame:
    # 创建评估模型
    evaluator = NetworkEvaluator(dataset)
    print("-----------------------------------------------")

    # 执行评估
    result = evaluator.full_evaluation({
        'degree_centrality': 0.4,
        'betweenness_centrality': 0.4,
        'closeness_centrality': 0.3,
        'eigenvector_centrality': 0.3,
        'pagerank': 0.3
    })

    print("\nTop 10 important nodes:")
    print(result.head(10))

    return result
