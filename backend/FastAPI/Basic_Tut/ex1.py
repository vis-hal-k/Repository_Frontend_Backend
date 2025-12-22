from fastapi import FastAPI, Path 
import json 
from pydantic import typing 


app = FastAPI() 

def load_data():
    with open('patient.json' , 'r') as f:
        data = json.load(f)
    return data
load_data()


@app.get("/") 
def hello():
    return {"messages" : "Hello World"}


@app.get('/patient/{patient_id}')
def view_patient(patient_id : str = Path(... , description='ID of the patient in the DB', example='P001') ):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    return {"error" : "patient not found"}
