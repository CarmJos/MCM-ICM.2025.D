from typing import Dict

import networkit as nk
import numpy as np
import pandas as pd
from tqdm import tqdm

from data.dataset import Dataset


def _build_networkit_graph(dataset: Dataset) -> nk.Graph:
    g = nk.Graph(len(dataset.nodes), directed=False)
    node_mapping = {node.id: i for i, node in enumerate(dataset.nodes)}

    for edge in tqdm(dataset.edges, desc="BUILDING"):
        u = node_mapping[edge.u]
        v = node_mapping[edge.v]
        if edge.oneway:
            if edge.reversed:
                g.addEdge(v, u)  # 从v到u
            else:
                g.addEdge(u, v)  # 从u到v
        else:  # 双向边
            g.addEdge(u, v)
            g.addEdge(v, u)
    return g


def _calculate_degree_centrality(dataset: Dataset, graph: nk.Graph) -> Dict[int, float]:
    print("Calculating degree centrality...")
    deg_centrality = nk.centrality.DegreeCentrality(graph)
    deg_centrality.run()
    return {node.id: deg_centrality.score(i) for i, node in enumerate(dataset.nodes)}


def _calculate_betweenness_centrality(dataset: Dataset, graph: nk.Graph) -> Dict[int, float]:
    print("Calculating betweenness centrality...")
    bet_centrality = nk.centrality.Betweenness(graph, normalized=True)
    bet_centrality.run()
    return {node.id: bet_centrality.score(i) for i, node in enumerate(dataset.nodes)}


def _calculate_closeness_centrality(dataset: Dataset, graph: nk.Graph) -> Dict[int, float]:
    print("Calculating closeness centrality...")
    closeness_centrality = nk.centrality.Closeness(graph, True, True)
    closeness_centrality.run()
    return {node.id: closeness_centrality.score(i) for i, node in enumerate(dataset.nodes)}


def _calculate_eigenvector_centrality(dataset: Dataset, graph: nk.Graph) -> Dict[int, float]:
    print("Calculating eigenvector centrality...")
    try:
        eigen_centrality = nk.centrality.EigenvectorCentrality(graph)
        eigen_centrality.run()
        return {node.id: eigen_centrality.score(i) for i, node in enumerate(dataset.nodes)}
    except Exception as e:
        print(f"Error: {e}")
        return {}


def _calculate_pagerank(dataset: Dataset, graph: nk.Graph) -> Dict[int, float]:
    print("Calculating PageRank...")
    pagerank = nk.centrality.PageRank(graph, damp=0.85)
    pagerank.run()
    return {node.id: pagerank.score(i) for i, node in enumerate(dataset.nodes)}


def calculate_metrics(dataset: Dataset) -> pd.DataFrame:
    graph = _build_networkit_graph(dataset)

    metrics = {
        'degree_centrality': _calculate_degree_centrality(dataset, graph),
        'betweenness_centrality': _calculate_betweenness_centrality(dataset, graph),
        'closeness_centrality': _calculate_closeness_centrality(dataset, graph),
        'eigenvector_centrality': _calculate_eigenvector_centrality(dataset, graph),
        'pagerank': _calculate_pagerank(dataset, graph)
    }

    # Convert metrics(type: [{id:float},.....]) to DataFrame, unique node_id as index, and each metric as a column
    metrics_df = pd.DataFrame(metrics)
    metrics_df['node'] = metrics_df.index
    metrics_df.set_index('node', inplace=True)

    return metrics_df


def load_metrics(metrics_path: str) -> pd.DataFrame:
    """加载节点度量数据"""
    return pd.read_csv(metrics_path, index_col='node', low_memory=False)


def topsis_evaluate(
        metrics: pd.DataFrame, weights: Dict[str, float] = None
) -> Dict[int, float]:
    """基于余弦相似性TOPSIS法的节点综合评估"""
    node = metrics.index
    # 提取指标列（排除node列）
    metric_columns = [col for col in metrics.columns if col != "node"]
    data = metrics[metric_columns].values

    # 处理权重（默认等权重）
    if not weights:
        weights = {col: 1.0 / len(metric_columns) for col in metric_columns}
    ordered_weights = np.array([weights[col] for col in metric_columns])

    # 规范化：每个指标除以列L2范数
    norm_data = data / np.linalg.norm(data, axis=0, keepdims=True)

    # 应用权重
    weighted_data = norm_data * ordered_weights

    # 确定最优解和最劣解（假设所有指标为效益型）
    positive_ideal = np.max(weighted_data, axis=0)
    negative_ideal = np.min(weighted_data, axis=0)

    # 计算余弦相似度
    pos_dot = weighted_data @ positive_ideal
    neg_dot = weighted_data @ negative_ideal

    data_norms = np.linalg.norm(weighted_data, axis=1)
    pos_ideal_norm = np.linalg.norm(positive_ideal)
    neg_ideal_norm = np.linalg.norm(negative_ideal)

    # 避免除以零
    epsilon = 1e-10
    pos_sim = pos_dot / (data_norms * pos_ideal_norm + epsilon)
    neg_sim = neg_dot / (data_norms * neg_ideal_norm + epsilon)

    # 转换为距离
    pos_distance = 1 - pos_sim
    neg_distance = 1 - neg_sim

    # 计算贴近度
    closeness = neg_distance / (pos_distance + neg_distance + epsilon)

    # 构建结果字典 {node_id: topsis_score}
    return dict(zip(node, closeness))
