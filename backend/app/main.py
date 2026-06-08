from fastapi import FastAPI
import joblib
from pathlib import Path
import pandas as pd 
import datetime
app = FastAPI()

base_dir = Path(__file__).resolve().parents[2]
model_path = base_dir / "ml" / "models" / "pit_model.pkl"

model = joblib.load(model_path)



@app.get("/health")
def health():
    return{
        "status": "healthy",
        "timestamp": datetime.datetime.now()
    }

@app.post("/predict")
def predict(data: dict):

    df = pd.DataFrame([data])

    prediction = model.predict_proba(df)[0][1]

    return {
        "pit_probability": float(prediction)
    }