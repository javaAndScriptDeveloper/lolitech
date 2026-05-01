import datetime
import json
import matplotlib.pyplot as plt
from config import PLOTS_FOLDER, HYPERPARAMS_ACCURACY_PATH

def plot_accuracy_vs_hyperparams(records):
    # Extract hyperparameters and accuracy from records
    hyperparams_list = [record['hyperparams'] for record in records]
    accuracy_list = [record['accuracy'] for record in records]

    # Plotting
    plt.figure(figsize=(12, 6))

    # Plotting for each hyperparameter
    for param_name in hyperparams_list[0]:
        param_values = [params[param_name] for params in hyperparams_list]
        plt.plot(param_values, accuracy_list, 'o-', label=f'{param_name}')

    plt.xlabel('Hyperparameter Values')
    plt.ylabel('Accuracy')
    plt.title('Accuracy vs Hyperparameters')
    plt.legend()
    plt.grid(True)
    plot_filename = f'{PLOTS_FOLDER}/accuracy_vs_hyperparams_plot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
    plt.savefig(plot_filename)


with open(HYPERPARAMS_ACCURACY_PATH, 'r') as f:
    records_data = json.load(f)
    records = records_data.get('records', [])

plot_accuracy_vs_hyperparams(records)