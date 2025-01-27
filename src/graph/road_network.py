import pandas as pd
from matplotlib import pyplot as plt
from data.dataset import Dataset
import folium


def draw_network(dataset: Dataset):
    fig, ax = plt.subplots(dpi=300, figsize=(20, 20))  # 设置图形大小，单位为英寸
    dataset.table_edges.plot(ax=ax, linewidth=0.5, color='gray', alpha=0.5)
    dataset.table_nodes.plot(ax=ax, markersize=0.5, color='red', alpha=0.5)
    dataset.table_bus_stops.plot(ax=ax, markersize=0.75, color='blue')

    plt.show()


def draw_important_nodes(dataset: Dataset, df: pd.DataFrame, limit: int) -> folium.Map:
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
