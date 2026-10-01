import torch
from torchvision import transforms
from PIL import Image
import io
from .model import SimpleCNN
from typing import List

class ModelPredictor:
    def __init__(self, model_path: str = "checkpoints/model.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SimpleCNN(num_classes=10)
        
        import os
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            
        self.model.to(self.device)
        self.model.eval()
        
        self.transform = transforms.Compose([
            transforms.Grayscale(num_output_channels=1),
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])

    def predict_image(self, image_bytes: bytes) -> List[float]:
        image = Image.open(io.BytesIO(image_bytes))
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
        return probabilities[0].tolist()
