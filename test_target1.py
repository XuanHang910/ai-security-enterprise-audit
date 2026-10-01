import torch
from torchvision import datasets, transforms
from PIL import Image
import requests
import io
import os

def test_target1():
    print("Preparing test image...")
    transform = transforms.ToTensor()
    dataset = datasets.FashionMNIST('data', train=False, download=True, transform=transform)
    img, label = dataset[0]
    img = transforms.ToPILImage()(img)
    img.save("sample.jpg")

    url = "http://127.0.0.1:8001/predict"
    print(f"Sending request to {url}...")
    try:
        with open("sample.jpg", "rb") as f:
            files = {"file": ("sample.jpg", f, "image/jpeg")}
            response = requests.post(url, files=files)
        print("Target 1 Response Status:", response.status_code)
        print("Target 1 Response Data:", response.json())
    except Exception as e:
        print("Error connecting to Target 1:", e)
    finally:
        if os.path.exists("sample.jpg"):
            os.remove("sample.jpg")

if __name__ == "__main__":
    test_target1()
