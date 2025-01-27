from matplotlib import pyplot as plt
from data.dataset import Dataset


def draw_network(dataset: Dataset):
    fig, ax = plt.subplots(dpi=300, figsize=(20, 20))  # 设置图形大小，单位为英寸
    dataset.table_edges.plot(ax=ax, linewidth=0.5, color='gray', alpha=0.5)
    dataset.table_nodes.plot(ax=ax, markersize=0.5, color='red', alpha=0.5)
    dataset.table_bus_stops.plot(ax=ax, markersize=0.75, color='blue')

    plt.show()
