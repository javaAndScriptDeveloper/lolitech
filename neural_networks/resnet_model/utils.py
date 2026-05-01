import json
import logging
import time
import torch.nn as nn
from matplotlib import pyplot as plt
from torchvision import datasets, transforms, models

from src.resnet_model.config import HYPERPARAMS_ACCURACY_PATH

def log_training_time(start_time):
    end_time = time.time()
    training_time = end_time - start_time
    logging.log(f"Training time: {training_time:.2f} seconds")
    print(f"Training time: {training_time:.2f} seconds")


def save_hyperparams_accuracy(hyperparams, accuracy):
    with open(HYPERPARAMS_ACCURACY_PATH, 'r') as f:
        records_data = json.load(f)
        records = records_data.get('records', [])

    records.append({
        "accuracy": accuracy,
        "hyperparams": {
            "lr": hyperparams["lr"],
            "momentum": hyperparams["momentum"]
        }
    })

    with open(HYPERPARAMS_ACCURACY_PATH, 'w') as f:
        json.dump({'records': records}, f, indent=2)

# Define the model
class CustomResNet(nn.Module):
    def __init__(self, num_classes):
        super(CustomResNet, self).__init__()
        resnet = models.resnet18(pretrained=True)
        resnet.fc = nn.Linear(resnet.fc.in_features, num_classes)
        self.resnet = resnet

    def forward(self, x):
        return self.resnet(x)

def plot_results(train_losses, val_losses, val_accuracies):
    # Plot the training metrics
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(val_accuracies, label='Validation Accuracy', color='orange')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.tight_layout()
    plt.savefig('training_plots.png')
    plt.show()
