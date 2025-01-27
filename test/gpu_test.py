import torch

if __name__ == '__main__':
    print(f"Active GPU devices ({torch.cuda.device_count()}): ")
    for i in range(torch.cuda.device_count()):
        print(f"#{i} {torch.cuda.get_device_name(i)}")
