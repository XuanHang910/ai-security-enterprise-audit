import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from target1_pytorch_classifier.model import SimpleCNN
from art.estimators.classification import PyTorchClassifier
from art.attacks.evasion import FastGradientMethod

def train_adversarial(epochs=1, save_path="checkpoints/model_adv.pth"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleCNN(num_classes=10).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    transform = transforms.Compose([transforms.ToTensor()])
    train_dataset = datasets.FashionMNIST('data', train=True, download=True, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

    classifier = PyTorchClassifier(
        model=model, clip_values=(0.0, 1.0), loss=criterion,
        optimizer=optimizer, input_shape=(1, 28, 28), nb_classes=10,
        device_type='gpu' if torch.cuda.is_available() else 'cpu'
    )
    
    attack = FastGradientMethod(estimator=classifier, eps=0.1)
    
    model.train()
    print("Starting Adversarial Training...")
    for epoch in range(epochs):
        for batch_idx, (data, target) in enumerate(train_loader):
            data_np, target_np = data.numpy(), target.numpy()
            
            # Generate adversarial examples on the fly
            adv_data = attack.generate(x=data_np)
            
            # Combine clean and adversarial data
            combined_data = torch.tensor(np.concatenate([data_np, adv_data])).to(device)
            combined_target = torch.tensor(np.concatenate([target_np, target_np])).to(device)
            
            optimizer.zero_grad()
            output = model(combined_data)
            loss = criterion(output, combined_target)
            loss.backward()
            optimizer.step()
            
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"Adversarially trained model saved to {save_path}")
    return model

if __name__ == "__main__":
    train_adversarial()
