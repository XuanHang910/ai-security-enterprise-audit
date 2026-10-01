from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict
from .inference import ModelPredictor

app = FastAPI(title="Target 1: PyTorch Classifier API", description="API for testing Robustness and Privacy")
predictor = ModelPredictor()

class PredictionResponse(BaseModel):
    probabilities: List[float]
    predicted_class: int

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)) -> Dict:
    image_bytes = await file.read()
    probabilities = predictor.predict_image(image_bytes)
    predicted_class = probabilities.index(max(probabilities))
    
    return {
        "probabilities": probabilities,
        "predicted_class": predicted_class
    }
