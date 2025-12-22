import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal  # to add description to the fields
app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str,Field(...,description="ID of the patien" , examples=['P001'])]
    name: Annotated[str,Field(...,description="Name of the patient")]
    city: Annotated[str,Field(...,description="City where the patient lives")]
    age: Annotated[int,Field(...,gt=0,lt=120, description="Age of the patient")]
    gender: Annotated[Literal["male","female"],Field(...,description="Gender of the patient")]
    height: Annotated[float,Field(...,gt=0,description="Height of the patient in meters")]
    weight: Annotated[float,Field(...,gt=0,description="Weight of the patient in kilograms")]

    # bmi is computed field
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2),2)
        return bmi  
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Normal" 
        elif self.bmi < 35:
            return "Obese"

def load_data():
    with open('patient.json','r') as f:
        data = json.load(f)
    return data
    
@app.get('/')
def start():
    return {"Message" : "Welcome to the patient API"}
@app.get('/patient_data')
def get_p_data():
    data = load_data()
    return JSONResponse(
        status_code=200 ,
        content= data
    )
    
@app.post('/patient')
def create_patient(patient: Patient):
    # load data
    loaded_data = load_data()
    # Check if the patient id already exists
    if patient.id in loaded_data:
        raise HTTPException(
            status_code=400,
            detail = "Patient already exits"
        )
    # new patient add to the database 
    # Remember : patient is pydantic object but loaded_data is json.
    loaded_data[patient.id] = patient.model_dump(exclude=['id'])      # this model_dump is convert pydantic object into dict.
    # save the data to the json file. 
    with open('patient.json','w') as f:
        json.dump(loaded_data,f)

    return JSONResponse(
        status_code = 201, # 201 is when a resource is created.
        content = {
            "message" : "Patient created successfully",
            "data" : {"bmi" : patient.bmi,
                      "verdict" : patient.verdict}
        }
    )   