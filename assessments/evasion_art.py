import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
import numpy as np
from art.estimators.classification import PyTorchClassifier
from art.attacks.evasion import FastGradientMethod, ProjectedGradientDescent
import sys
import os

# Ensure parent directory is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from target1_pytorch_classifier.model import SimpleCNN
from assessments.audit_logger import AuditLogger

def run_evasion_tests():
    logger = AuditLogger()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleCNN(num_classes=10)
    try:
        model.load_state_dict(torch.load("checkpoints/model.pth", map_location=device))
    except Exception as e:
        print(f"Warning: Could not load model checkpoint ({e}). Using random weights.")
    model.to(device)
    model.eval()

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    classifier = PyTorchClassifier(
        model=model,
        clip_values=(0.0, 1.0),
        loss=criterion,
        optimizer=optimizer,
        input_shape=(1, 28, 28),
        nb_classes=10,
        device_type='gpu' if torch.cuda.is_available() else 'cpu'
    )

    transform = transforms.Compose([transforms.ToTensor()])
    test_dataset = datasets.FashionMNIST('data', train=False, download=True, transform=transform)
    x_test = test_dataset.data.numpy()[:100].reshape(-1, 1, 28, 28).astype(np.float32) / 255.0
    y_test = test_dataset.targets.numpy()[:100]

    predictions = classifier.predict(x_test)
    baseline_acc = np.mean(np.argmax(predictions, axis=1) == y_test)
    
    epsilons = [0.05, 0.1, 0.2]
    results = {"baseline_accuracy": float(baseline_acc), "FGSM": {}, "PGD": {}}

    print(f"Baseline Accuracy: {baseline_acc*100:.2f}%")

    for eps in epsilons:
        attack_fgsm = FastGradientMethod(estimator=classifier, eps=eps)
        x_test_adv_fgsm = attack_fgsm.generate(x=x_test)
        preds_fgsm = classifier.predict(x_test_adv_fgsm)
        acc_fgsm = np.mean(np.argmax(preds_fgsm, axis=1) == y_test)
        results["FGSM"][str(eps)] = float(acc_fgsm)
        
        attack_pgd = ProjectedGradientDescent(estimator=classifier, eps=eps, eps_step=0.01, max_iter=10)
        x_test_adv_pgd = attack_pgd.generate(x=x_test)
        preds_pgd = classifier.predict(x_test_adv_pgd)
        acc_pgd = np.mean(np.argmax(preds_pgd, axis=1) == y_test)
        results["PGD"][str(eps)] = float(acc_pgd)

        print(f"Epsilon: {eps} | FGSM Acc: {acc_fgsm*100:.2f}% | PGD Acc: {acc_pgd*100:.2f}%")

    logger.log_result("Target 1", "Adversarial Evasion (MITRE ATLAS AML.T0015)", results)

if __name__ == "__main__":
    run_evasion_tests()
