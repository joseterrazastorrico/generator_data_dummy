from fastapi import FastAPI, Form, File, UploadFile
from pydantic import BaseModel
import pandas as pd
import numpy as np
from typing import List
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import random

app = FastAPI()

class DataVariable(BaseModel):
    name: str
    min_value: float
    max_value: float
    mean_value: float
    start: str
    end: str
    distribution: str = 'normal'
    frequency: str  = '5min'


def calcular_pasos(start: str, end: str, frequency: str) -> int:
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)
    freq_timedelta = pd.to_timedelta(frequency)

    pasos = (end_dt - start_dt) // freq_timedelta + 1
    return pasos


def generate_data(variable: DataVariable):
    time_span = calcular_pasos(variable.start, variable.end, variable.frequency)
    if variable.distribution == 'uniform':
        data = np.random.uniform(variable.min_value, variable.max_value, time_span)
    elif variable.distribution == 'normal':
        data = np.random.normal(variable.mean_value, (variable.max_value - variable.min_value) / 6, time_span)
    elif variable.distribution == 'poisson':
        data = np.random.poisson(variable.mean_value, time_span)
    elif variable.distribution == 'binary':
        data = np.random.choice([0, 1], size=time_span, replace=True, p=[1 - variable.mean_value, variable.mean_value])
    else:
        raise ValueError(f"Distribución {variable.distribution} no soportada.")
    
    dates = pd.date_range(start=variable.start, end=variable.end, freq=variable.frequency)
    df = pd.DataFrame(data, columns=[variable.name], index=dates)

    return df


@app.post("/generate_data/")
async def generate_data_endpoint(variables: List[DataVariable]):
    try:
        all_data = []
        for var in variables:
            df = generate_data(var)
            all_data.append(df)
        
        final_df = pd.concat(all_data, axis=1)
        
        sample = final_df.to_dict()
        return JSONResponse(content=jsonable_encoder(sample))
    
    except Exception as e:
        print(e)
        return JSONResponse(status_code=400, content={"message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
