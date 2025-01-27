import math
from cmath import isnan
from typing import Callable

import folium
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.cm import ScalarMappable

from data.dataset import Dataset
from data.traffic import TrafficSet, TrafficData
from model.metrics import topsis_evaluate, load_metrics


def colormap(val: float, min_num: float, max_num: float) -> str:
    normalized_val = (math.sqrt(val) - math.sqrt(min_num)) / (math.sqrt(max_num) - math.sqrt(min_num))
    normalized_val = max(0, min(1, normalized_val))  # 限制在 [0, 1] 范围内
    cmap = plt.get_cmap("RdYlGn")  # 'RdYlGn' 是红黄绿的渐变色
    norm = mcolors.Normalize(vmin=0, vmax=1)  # 归一化到 [0, 1]
    sm = ScalarMappable(cmap=cmap, norm=norm)  # 生成颜色映射
    color = sm.to_rgba(1 - normalized_val)  # 转换为RGBA格式
    return mcolors.rgb2hex(color)  # 转换为十六进制颜色代码


def draw_network(dataset: Dataset):
    fig, ax = plt.subplots(dpi=300, figsize=(20, 20))  # 设置图形大小，单位为英寸
    dataset.table_edges.plot(ax=ax, linewidth=0.5, color='gray', alpha=0.5)
    dataset.table_nodes.plot(ax=ax, markersize=0.5, color='red', alpha=0.5)

    plt.show()


def draw_important(dataset: Dataset):
    metrics = load_metrics('../data/processed/metrics.csv')
    scores = topsis_evaluate(metrics, {
        "degree_centrality": 0.3,
        "betweenness_centrality": 0.3,
        "closeness_centrality": 0.2,
        "eigenvector_centrality": 0.1,
        "pagerank": 0.1
    })
    scores_df = pd.DataFrame(scores.items(), columns=['node', 'score'])
    scores_df = scores_df.sort_values('score', ascending=False)
    _draw_important_nodes(dataset, scores_df, 50).save('../target/important_nodes.html')


def _draw_important_nodes(dataset: Dataset, df: pd.DataFrame, limit: int) -> folium.Map:
    # 将重要性数据转换为 GeoDataFrame
    df = dataset.table_nodes.merge(df, left_on='osmid', right_on='node')

    # 按照 score 降序排序
    df = df.sort_values('score', ascending=False)

    # 取出前 limit 个节点
    df = df.head(limit)

    # 创建地图，以df中所有节点的平均经纬度为中心，经纬度从geometry列中获取
    m = folium.Map(location=[df.geometry.y.mean(), df.geometry.x.mean()], zoom_start=15)

    color_map = ['lightgreen', 'green', 'darkgreen', 'lightblue', 'darkblue']

    max_score = df['score'].max()
    min_score = df['score'].min()
    score_range = max_score - min_score

    def color(score):
        if score == max_score:
            return color_map[4]
        if score == min_score:
            return color_map[0]
        return color_map[int((score - min_score) / score_range * 5)]

    # 添加节点到地图中，每个节点都标记其名称和分数，颜色根据分数的高低而变化
    for index, row in df.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"{row['score']:.4f}",
            icon=folium.Icon(color=color(row['score']), icon='info-sign')
        ).add_to(m)

    return m


def draw_traffic_map(dataset: Dataset, traffic: TrafficSet,
                     traffic_extractor: Callable[[TrafficData], float]):
    node_traffics = traffic.build_node_traffic_dict(traffic_extractor)
    print(f"Traffic data loaded for {len(node_traffics)} nodes.")

    # 将 node_traffics 转换成为 Node: float, 以便于后续的评估
    # 若 dataset.node(k) 不存在，则忽略
    node_traffics = {dataset.node(k): v for k, v in node_traffics.items() if dataset.node(k) and not isnan(v)}

    # 如果有节点没有流量数据，则返回空地图
    if len(node_traffics) == 0:
        print("No traffic data available.")
        return folium.Map(location=[dataset.nodes[0].point.y, dataset.nodes[0].point.x], zoom_start=12)

    # 初始化地图（以nodes的第一个点为中心）
    first_node = dataset.nodes[0].point
    m = folium.Map(location=[first_node.y, first_node.x], zoom_start=12)

    # 获取所有边的流量值并生成颜色映射
    traffic_values = list(node_traffics.values())
    min_traffic = min(traffic_values)
    max_traffic = max(traffic_values)  # 使用平方根函数来让颜色变化先快后慢

    # 生成颜色映射（绿->黄->红；渐变）
    def _color(val: float):
        return colormap(val, min_traffic, max_traffic)

    print(f"Traffic range: {min_traffic} - {max_traffic}")

    # 添加所有边到地图
    for node, traffic in node_traffics.items():
        folium.Circle(
            location=[node.point.y, node.point.x],
            radius=100,  # 流量越大圆越大
            color=_color(traffic),
            opacity=(0.8 if traffic > 0 else 0.3),
            fill=True,
            tooltip=f"""
            {node.id}<br>
            {traffic:.0f}<br>
            """
        ).add_to(m)

    return m
