import datetime
from time import sleep

from data.dataset import *
from data.metrics import load_metrics, topsis_evaluate, calculate_metrics
from graph.road_network import draw_important_nodes


def cal_metrics():
    print("Calculating metrics...")
    start_time = datetime.datetime.now()
    calculate_metrics(dataset).to_csv('../target/metrics.csv')
    print(f"Metrics calculated in {(datetime.datetime.now() - start_time).seconds} seconds")


def draw_important():
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
    draw_important_nodes(dataset, scores_df, 50).save('../target/important_nodes.html')


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

    print("-----------------------------------------------")

    # cal_metrics()
    # draw_important()

