import numpy as np
from sklearn.ensemble import IsolationForest
from torchvision import datasets, transforms

def sanitize_dataset(dataset):
    print("Sanitizing dataset with Isolation Forest...")
    # Flatten images for feature representation
    x_data = dataset.data.numpy().reshape(len(dataset), -1).astype(np.float32) / 255.0
    
    # Using Isolation Forest to detect anomalies (outliers)
    clf = IsolationForest(contamination=0.05, random_state=42)
    predictions = clf.fit_predict(x_data)
    
    # 1 for inliers, -1 for outliers
    clean_indices = np.where(predictions == 1)[0]
    poison_indices = np.where(predictions == -1)[0]
    
    print(f"Original dataset size: {len(dataset)}")
    print(f"Clean samples retained: {len(clean_indices)}")
    print(f"Anomalous samples removed: {len(poison_indices)}")
    
    return clean_indices

if __name__ == "__main__":
    transform = transforms.Compose([transforms.ToTensor()])
    dataset = datasets.FashionMNIST('data', train=True, download=True, transform=transform)
    sanitize_dataset(dataset)
