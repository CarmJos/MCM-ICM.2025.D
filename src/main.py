import datetime
from time import sleep

from data.traffic import TrafficSet
from graph.road_network import draw_traffic_map
from model.metrics import *


def cal_metrics():
    print("Calculating metrics...")
    start_time = datetime.datetime.now()
    calculate_metrics(dataset).to_csv('../target/metrics.csv')
    print(f"Metrics calculated in {(datetime.datetime.now() - start_time).seconds} seconds")


if __name__ == '__main__':
    print("-----------------------------------------------")
    print("Initializing dataset...")
    dataset = Dataset()
    print("Loading dataset...")
    start_time = datetime.datetime.now()
    dataset.load()
    print(f"Dataset loaded in {(datetime.datetime.now() - start_time).seconds} seconds")
    print("-----------------------------------------------")
    sleep(1)

    # 创建评价模型并执行分析
    traffic = TrafficSet()

    for i in range(2014, 2022):
        print(f"Processing traffic data for year {i}...")
        draw_traffic_map(dataset, traffic, (lambda d: d.aadt(i))).save(f"../target/traffic_aadt_{i}.html")

    for i in range(2014, 2022):
        print(f"Processing traffic data for year {i}...")
        draw_traffic_map(dataset, traffic, (lambda d: d.aawdt(i))).save(f"../target/traffic_aawdt_{i}.html")

    draw_traffic_map(dataset, traffic, (lambda d: d.aadt(i))).save(f"../target/traffic_aadt_current.html")
    draw_traffic_map(dataset, traffic, (lambda d: d.aawdt(i))).save(f"../target/traffic_aawdt_current.html")

    # 生成报告

    # cal_metrics()
    # draw_important()
