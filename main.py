from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import pickle

from ml.data import process_data
from ml.model import inference

import uvicorn


# Load models
model_paths = {'model':'model/model.pkl','encoder':'model/encoder.pkl','lb':'model/lb.pkl'}
models = dict.fromkeys(model_paths)
for path_key,path in model_paths.items():
    with open(path,'rb') as f:
        models[path_key] = pickle.load(f)


# Help function to replace underbar back to dash
def rep_ubar_to_dash(col: str) -> str:
    return col.replace('_','-')


# Data Class Definition
class CensusData(BaseModel):
    age: int
    workclass: str
    fnlgt: int
    education: str
    education_num: int
    marital_status: str
    occupation: str
    relationship: str
    race: str
    sex: str
    capital_gain: int
    capital_loss: int
    hours_per_week: int
    native_country: str
    salary: Optional[str]

    class Config:
        alias_generator = rep_ubar_to_dash


# Initialize FastAPI app
app = FastAPI()

# Show a welcome msg
@app.get('/')
async def welcome():
    return {'msg':'Welcome!'}

# Model Inference
@app.post('/predict')
async def predict(input: CensusData):
    """ Send POST request with input data

    Inputs
    ------
    input : CensusData
        Input Data

    Returns
    -------
     : dict
        Model Inference on Input Data
    """

    cat_features = [
    "workclass",
    "education",
    "marital-status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "native-country",
    ]

    # Prepare Data
    input_data = input.dict(by_alias=True)
    input_df = pd.DataFrame(input_data,index=[0])

    # Preprocess data
    X, y, encoder, lb = process_data(input_df, categorical_features=cat_features, label='salary', encoder=models['encoder'], lb=models['lb'], training=False)

    # Prediction
    preds = inference(models['model'], X)

    return {'result':int(preds[0])}

if __name__ == '__main__':
    uvicorn.run('main:app',reload=True)