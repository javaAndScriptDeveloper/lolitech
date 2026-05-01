# main.py
import torch.nn as nn
import torch.optim as optim
import time
import logging
import json
from tqdm import tqdm

from config import device, train_loader, val_loader, EPOCHS
from utils import CNNModel, train, validate, process_results, log_training_time, save_hyperparams_accuracy

# Manually set hyperparameter values
HYPERPARAMS = {
    'conv1_out_channels': 128,
    'conv2_out_channels': 256,
    'hidden_size': 256,
}

# Metadata
misclassified_images = []
train_losses = []
val_losses = []
val_accuracies = []

def process_trainig(hyperparams):
    global train_losses, val_losses, val_accuracies

    print(f"\nTraining with Hyperparameters: {hyperparams}")

    # Initialize the model with the current hyperparameters
    model = CNNModel(**hyperparams).to(device)

    # Initialize the criterion and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    train_losses_epoch = []
    val_losses_epoch = []
    val_accuracies_epoch = []

    for epoch in tqdm(range(EPOCHS), desc="Training"):
        train(model, train_loader, criterion, optimizer, device)
        train_loss, train_accuracy, _ = validate(model, train_loader, criterion, device)

        val_loss, val_accuracy, _ = validate(model, val_loader, criterion, device)

        train_losses_epoch.append(train_loss)
        val_losses_epoch.append(val_loss)
        val_accuracies_epoch.append(val_accuracy)

        logging.info(f"Epoch [{epoch + 1}/{EPOCHS}], "
                     f"Train Loss: {train_loss:.4f}, "
                     f"Validation Loss: {val_loss:.4f}, "
                     f"Validation Accuracy: {val_accuracy:.4f}")

    # Update global variables with epoch-averaged values
    train_losses = train_losses_epoch
    val_losses = val_losses_epoch
    val_accuracies = val_accuracies_epoch

    # Average results over epochs
    avg_val_accuracy = sum(val_accuracies_epoch) / len(val_accuracies_epoch)

    logging.info(f"Avg Validation Accuracy: {avg_val_accuracy:.4f}")

    # Save hyperparameter value for plotting
    return {'hyperparams': hyperparams, 'accuracy': avg_val_accuracy}, model

def main():

    training_start_time = time.time()

    # Train with tuning using manual hyperparameters
    hyperparams_accuracy, model = process_trainig(HYPERPARAMS)

    log_training_time(training_start_time)

    save_hyperparams_accuracy(hyperparams_accuracy)

    # Process results and generate plots
    process_results(train_losses, val_losses, val_accuracies, misclassified_images)

    #save_model(model)

if __name__ == "__main__":
    main()
