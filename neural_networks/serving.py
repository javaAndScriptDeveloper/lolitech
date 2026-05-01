from flask import Flask, request, jsonify
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import torch.nn.functional as F
import io

# Set up Flask
app = Flask(__name__)

MODEL = 'model_2023-11-12_02-24-24.pth' # Set here newly trained model

# Define the CNN model filled with hyperparameters from currently saved model
class CNNModel(nn.Module):
    def __init__(self):
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.fc1 = nn.Linear(128 * 7 * 7, 256)
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 128 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# Initialize the model and load the state dictionary
model = CNNModel()
model.load_state_dict(torch.load(MODEL, map_location=torch.device('cpu')))
model.eval()

# Define the image transformation
transform = transforms.Compose([transforms.Grayscale(), transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])


# Define the route for prediction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the image file from the request
        image_file = request.files['image']

        # Read the image file and transform it
        image = Image.open(io.BytesIO(image_file.read())).convert('L')
        image_tensor = transform(image).unsqueeze(0)

        # Make the prediction
        with torch.no_grad():
            output = model(image_tensor)
            _, predicted_class = torch.max(output, 1)

        # Return the prediction
        return jsonify({'predicted_class': int(predicted_class)})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
