import time

import torch
import torch.optim as optim
from torch import nn
from torchvision import datasets, transforms, models
import matplotlib.pyplot as plt
from tqdm import tqdm

from src.resnet_model.config import device, train_loader, train_dataset, val_loader, EPOCHS
from src.resnet_model.utils import log_training_time, CustomResNet, plot_results, save_hyperparams_accuracy

HYPERPARAMS = {
    "lr": 0.01,
    "momentum": 0.9
}


# Initialize the model, criterion, and optimizer
num_classes = len(train_dataset.classes)
model = CustomResNet(num_classes).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
train_losses = []
val_losses = []
val_accuracies = []


def process_training():
    global inputs, targets, outputs, loss
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        print(f"Training epoch: {epoch}")
        progress_bar = tqdm(enumerate(train_loader, 1), desc="Training", total=len(train_loader), leave=False)

        for batch_idx, (inputs, targets) in progress_bar:
            inputs, targets = inputs.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            progress_bar.set_postfix({'Epoch Loss': running_loss / batch_idx})

        avg_train_loss = running_loss / len(train_loader)
        train_losses.append(avg_train_loss)

        model.eval()
        val_loss = 0.0
        correct = 0
        total_samples = 0
        with torch.no_grad():
            progress_bar_val = tqdm(val_loader, desc="Validation", leave=False)
            for inputs, targets in progress_bar_val:
                inputs, targets = inputs.to(device), targets.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, targets)
                val_loss += loss.item()

                _, predicted = torch.max(outputs, 1)
                correct += (predicted == targets).sum().item()
                total_samples += targets.size(0)

        avg_val_loss = val_loss / len(val_loader)
        val_losses.append(avg_val_loss)

        val_accuracy = correct / total_samples
        val_accuracies.append(val_accuracy)

        print(f'Epoch {epoch + 1}/{EPOCHS}, '
              f'Training Loss: {avg_train_loss:.4f}, '
              f'Validation Loss: {avg_val_loss:.4f}, '
              f'Validation Accuracy: {val_accuracy:.4f}')
        return val_accuracy, model


def main():

    start_time = time.time()

    accuracy, model = process_training()

    log_training_time(start_time)

    plot_results(train_losses, val_losses, val_accuracies)

    save_hyperparams_accuracy(HYPERPARAMS, accuracy)

    #save_model(model)

if __name__ == "__main__":
    main()



