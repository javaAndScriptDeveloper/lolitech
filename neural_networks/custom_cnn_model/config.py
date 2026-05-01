import logging
import os

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# Folder to save plots
PLOTS_FOLDER = 'plots'

METADATA_FOLDER = 'metadata'

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
EPOCHS = 5

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load dataset
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
train_dataset = datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
val_dataset = datasets.FashionMNIST(root='./data', train=False, download=True, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)