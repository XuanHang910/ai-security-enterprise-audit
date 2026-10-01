import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from target1_pytorch_classifier.model import SimpleCNN

class PrivacyPreservingCNN(SimpleCNN):
    def __init__(self, num_classes=10):
        super(PrivacyPreservingCNN, self).__init__(num_classes)
        # Adding dropout to control overfitting and reduce privacy risks
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout(0.5)

    def forward(self, x):
        import torch.nn.functional as F
        x = self.pool(F.relu(self.conv1(x)))
        x = self.dropout1(x)
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.dropout2(x)
        x = self.fc2(x)
        return x

def train_privacy_model(epochs=1, save_path="checkpoints/model_privacy.pth"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = PrivacyPreservingCNN(num_classes=10).to(device)
    
    criterion = nn.CrossEntropyLoss()
    # Weight decay added to optimizer to prevent overfitting
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)

    transform = transforms.Compose([transforms.ToTensor()])
    train_dataset = datasets.FashionMNIST('data', train=True, download=True, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

    model.train()
    print("Training Privacy Preserving Model (Dropout + Weight Decay)...")
    for epoch in range(epochs):
        for data, target in train_loader:
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"Privacy model saved to {save_path}")
    return model

if __name__ == "__main__":
    train_privacy_model()
