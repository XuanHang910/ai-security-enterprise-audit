import torch
import numpy as np
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from target1_pytorch_classifier.model import SimpleCNN
from assessments.audit_logger import AuditLogger

def run_membership_inference():
    logger = AuditLogger()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = SimpleCNN(num_classes=10).to(device)
    try:
        model.load_state_dict(torch.load("checkpoints/model.pth", map_location=device))
    except:
        pass
    model.eval()
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    train_dataset = datasets.FashionMNIST('data', train=True, download=True, transform=transform)
    test_dataset = datasets.FashionMNIST('data', train=False, download=True, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=200, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=200, shuffle=False)
    
    def get_confidence_scores(loader):
        confidences = []
        with torch.no_grad():
            for data, _ in loader:
                data = data.to(device)
                outputs = model(data)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                max_probs, _ = torch.max(probs, dim=1)
                confidences.extend(max_probs.cpu().numpy())
                if len(confidences) >= 500:
                    break
        return np.array(confidences[:500])

    print("Collecting confidence scores...")
    train_conf = get_confidence_scores(train_loader)
    test_conf = get_confidence_scores(test_loader)
    
    threshold = np.median(train_conf)
    
    y_true = np.concatenate([np.ones(len(train_conf)), np.zeros(len(test_conf))])
    y_pred = np.concatenate([train_conf > threshold, test_conf > threshold])
    
    mia_accuracy = accuracy_score(y_true, y_pred)
    
    print(f"Membership Inference Accuracy: {mia_accuracy*100:.2f}%")
    logger.log_result("Target 1", "Membership Inference (MITRE ATLAS AML.T0024)", {"mia_accuracy": float(mia_accuracy)})

if __name__ == "__main__":
    run_membership_inference()
