import datetime
from time import sleep

from data.dataset import *
from traffic_evaluator import evaluate

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

