import logging
import os

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# Folder to save plots
PLOTS_FOLDER = 'plots'

# Folder to save metadata
METADATA_FOLDER = 'metadata'

# Folder to save hyperparams_accuracy
HYPERPARAMS_ACCURACY_FILE_NAME = "hyperparams_accuracy"

HYPERPARAMS_ACCURACY_PATH = METADATA_FOLDER + "/" + HYPERPARAMS_ACCURACY_FILE_NAME + ".json"

# Create folders
def create_metadata_folder():
    folders = [METADATA_FOLDER, PLOTS_FOLDER]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

# Set up logging
logging_file_path = METADATA_FOLDER + "/training.log"
logging.basicConfig(filename=logging_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Set number of epochs
EPOCHS = 4

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define data transformations
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


# Download and load CIFAR-10 dataset
root = "./data"
train_dataset = datasets.CIFAR10(root=root, train=True, download=True, transform=train_transform)
val_dataset = datasets.CIFAR10(root=root, train=False, download=True, transform=val_transform)

# Define dataloaders
batch_size = 64
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size, shuffle=False)