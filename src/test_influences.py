import pandas as pd
import networkx as nx
from _references import *

# 读取节点数据，包含节点ID、纬度和经度
nodes_df = pd.read_csv(NODES_FILE, usecols=[0, 1, 2], header=None, names=['node_id', 'latitude', 'longitude'],
                       skiprows=1)

# 筛选符合条件的节点
nodes_df = nodes_df[
    (nodes_df['latitude'] >= 39.18) & (nodes_df['latitude'] <= 39.33) &
    (nodes_df['longitude'] >= -76.71) & (nodes_df['longitude'] <= -76.45)
    ]

# 读取边数据
edges_df = pd.read_csv(NAMES_FILE, header=None, names=['street_name', 'nodes'], skiprows=1)

edges_df.head()

# 删除包含空值的行
edges_df = edges_df.dropna(subset=['nodes'])


def convert_nodes_to_list(nodes_str):
    # 去掉大括号和方括号
    nodes_str = nodes_str.strip('[]{}')
    # 如果节点列表为空或无效，返回空列表
    if not nodes_str or nodes_str == 'set()':
        return []
    # 按逗号分割并转换为整数列表
    try:
        return [int(node) for node in nodes_str.split(', ')]
    except ValueError:
        return []  # 如果转换失败，返回空列表


# 直接修改 edges_df 的 nodes 列
edges_df['nodes'] = edges_df['nodes'].apply(convert_nodes_to_list)
edges_df.head()

# 创建图
G = nx.Graph()

# 添加节点到图中，并附带纬度和经度信息
for _, row in nodes_df.iterrows():
    G.add_node(row['node_id'], latitude=row['latitude'], longitude=row['longitude'])

# 添加边到图中
for _, row in edges_df.iterrows():
    nodes = row['nodes']
    street_name = row['street_name']
    # 为每对相邻节点添加边
    for i in range(len(nodes) - 1):
        # 只添加两个节点都在筛选后的节点列表中的边
        if nodes[i] in G and nodes[i + 1] in G:
            G.add_edge(nodes[i], nodes[i + 1], street_name=street_name)

print(f"Number of nodes: {G.number_of_nodes()}")
print(f"Number of edges: {G.number_of_edges()}")
print(f"Average degree: {sum(dict(G.degree()).values()) / G.number_of_nodes()}")
