import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from target1_pytorch_classifier.model import SimpleCNN
from assessments.audit_logger import AuditLogger

def create_poisoned_data(dataset, target_class=9, trigger_size=4, poison_ratio=0.1):
    x_data = dataset.data.numpy().astype(np.float32) / 255.0
    y_data = dataset.targets.numpy()
    x_data = x_data.reshape(-1, 1, 28, 28)
    
    num_poison = int(len(x_data) * poison_ratio)
    poison_indices = np.random.choice(len(x_data), num_poison, replace=False)
    
    for idx in poison_indices:
        x_data[idx, 0, -trigger_size:, -trigger_size:] = 1.0 
        y_data[idx] = target_class
        
    return torch.tensor(x_data), torch.tensor(y_data), poison_indices

def run_poisoning_tests():
    logger = AuditLogger()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    transform = transforms.Compose([transforms.ToTensor()])
    train_dataset = datasets.FashionMNIST('data', train=True, download=True, transform=transform)
    test_dataset = datasets.FashionMNIST('data', train=False, download=True, transform=transform)
    
    x_train, y_train, _ = create_poisoned_data(train_dataset, target_class=9, poison_ratio=0.05)
    train_loader = DataLoader(TensorDataset(x_train, y_train), batch_size=64, shuffle=True)
    
    model = SimpleCNN(num_classes=10).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    model.train()
    print("Training poisoned model...")
    for epoch in range(1):
        for data, target in train_loader:
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
    x_test, y_test, _ = create_poisoned_data(test_dataset, target_class=9, poison_ratio=1.0)
    model.eval()
    with torch.no_grad():
        x_test = x_test.to(device)
        preds = torch.argmax(model(x_test), dim=1)
        asr = torch.mean((preds == 9).float()).item()
        
    print(f"Data Poisoning Attack Success Rate (ASR): {asr*100:.2f}%")
    logger.log_result("Target 1", "Data Poisoning / Backdoor (MITRE ATLAS AML.T0020)", {"ASR": float(asr)})

if __name__ == "__main__":
    run_poisoning_tests()
