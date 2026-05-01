import datetime
import json
import matplotlib.pyplot as plt

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
    plot_filename = f'accuracy_vs_hyperparams_plot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
    plt.savefig(plot_filename)
    plt.show()

file_path = "metadata/hyperparams_accuracy.json"  # Replace with the actual file path
with open(file_path, 'r') as file:
    data = json.load(file)

records = data.get("records", [])

# Plot accuracy vs hyperparameters
plot_accuracy_vs_hyperparams(records)
