# utils.py
import datetime
import json
import logging
import time

import torch
import torch.nn as nn
import torch.nn.functional as F
from matplotlib import pyplot as plt

from config import PLOTS_FOLDER, HYPERPARAMS_ACCURACY_PATH


# Define the CNN model
class CNNModel(nn.Module):
    def __init__(self, conv1_out_channels, conv2_out_channels, hidden_size):
        super(CNNModel, self).__init__()
        self.conv1_out_channels = conv1_out_channels
        self.conv2_out_channels = conv2_out_channels
        self.hidden_size = hidden_size

        self.conv1 = nn.Conv2d(1, self.conv1_out_channels, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(self.conv1_out_channels, self.conv2_out_channels, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.fc1 = nn.Linear(self.conv2_out_channels * 7 * 7, self.hidden_size)
        self.fc2 = nn.Linear(self.hidden_size, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, self.conv2_out_channels * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Function to train the model
def train(model, train_loader, criterion, optimizer, device):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

# Function to validate the model and track misclassified images
def validate(model, val_loader, criterion, device):
    model.eval()
    val_loss = 0
    correct = 0
    misclassified_images = []

    with torch.no_grad():
        for data, target in val_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            val_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

            # Track misclassified images
            misclassified_mask = pred.eq(target.view_as(pred)) == 0
            misclassified_indices = (misclassified_mask.nonzero())[:, 0]
            for mis_idx in misclassified_indices:
                misclassified_images.append({
                    'image': data[mis_idx].cpu().numpy(),
                    'true_label': target[mis_idx].item(),
                    'predicted_label': pred[mis_idx].item()
                })

    val_loss /= len(val_loader.dataset)
    accuracy = correct / len(val_loader.dataset)

    return val_loss, accuracy, misclassified_images

# Function to plot training results and save plot
def generate_training_plot(train_losses, val_losses, val_accuracies):
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(val_accuracies, label='Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.tight_layout()

    # Save plot with date-time included in the name
    plot_filename = f'{PLOTS_FOLDER}/training_plot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
    plt.savefig(plot_filename)
    plt.show()

def process_results(train_losses, val_losses, val_accuracies, misclassified_images):

    # Plot and save results
    generate_training_plot(train_losses, val_losses, val_accuracies)
    generate_misclassified_images_plot(misclassified_images)


def save_model(model):
    # Save the best model
    model_filename = f'model_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pth'
    torch.save(model, model_filename)

def log_training_time(start_time):
    training_time = time.time() - start_time
    logging.info(f"Training Time: {training_time} seconds")

def save_hyperparams_accuracy(hyperparams_accuracy):

    with open(HYPERPARAMS_ACCURACY_PATH, 'r') as f:
        records_data = json.load(f)
        records = records_data.get('records', [])

    records.append(hyperparams_accuracy)

    with open(HYPERPARAMS_ACCURACY_PATH, 'w') as f:
        json.dump({'records': records}, f, indent=2)

def generate_misclassified_images_plot(misclassified_images):
    plt.figure(figsize=(15, 3))
    # Display misclassified images
    for i, misclassified_image in enumerate(misclassified_images[:5]):
        plt.subplot(1, 5, i + 1)
        plt.imshow(misclassified_image['image'].squeeze(), cmap='gray')
        plt.title(f'True: {misclassified_image["true_label"]}, Predicted: {misclassified_image["predicted_label"]}')
        plt.axis('off')
    # Save the misclassified plot with date-time
    misclassified_plot_filename = f'{PLOTS_FOLDER}/misclassified_plot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
    plt.savefig(misclassified_plot_filename)
    plt.show()
