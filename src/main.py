import datetime
from time import sleep

from data.dataset import *
from model.topsis_evaluator import NetworkEvaluator

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

    # 创建评估模型
    evaluator = NetworkEvaluator(dataset)

    # 执行评估
    result = evaluator.full_evaluation(weights={
        'degree_centrality': 0.2,
        'betweenness_centrality': 0.2,
        'closeness_centrality': 0.15,
        'eigenvector_centrality': 0.15,
        'pagerank': 0.15,
        'connection_strength': 0.15
    })

    print("\nTop 10 important nodes:")
    print(result.head(10))
