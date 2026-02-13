import uvicorn
from fastapi import FastAPI
# from Wine import WineQuality
import numpy as np
# import pickle
import joblib
import pandas as pd

from pydantic import BaseModel

class WineQuality(BaseModel):
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides:float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float

app = FastAPI()
classifier = joblib.load("outputs/model/model.pkl")


@app.post('/predict')
def predict_quality(data: WineQuality):
    data = data.dict()
    fixed_acidity = data['fixed_acidity']
    volatile_acidity = data['volatile_acidity']
    citric_acid = data['citric_acid']
    residual_sugar = data['residual_sugar']
    chlorides = data['chlorides']
    free_sulfur_dioxide = data['free_sulfur_dioxide']
    total_sulfur_dioxide = data['total_sulfur_dioxide']
    density = data['density']
    pH = data['pH']
    sulphates = data['sulphates']
    alcohol = data['alcohol']

    prediction = classifier.predict([[fixed_acidity, volatile_acidity, citric_acid, residual_sugar, chlorides, free_sulfur_dioxide, total_sulfur_dioxide, density, pH, sulphates, alcohol]])
    return {
        'name':'nivitha noble',
        'roll num': '2022BCS0008',
        'prediction': prediction[0]
    }
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)