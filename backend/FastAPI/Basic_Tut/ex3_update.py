import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
from ex1 import load_data
from ex2_post import Patient
app = FastAPI()

class UpdatePatient(BaseModel):
    # id : Annotated(Optional[str], Field(...,description=""))
    # We don't take ids here because we take it through path parameter.
    name: Annotated[Optional[str],  Field(default=None,description="Name of the patient")]
    city: Annotated[Optional[str],  Field(default=None,description="City where the patient lives")]
    age: Annotated[Optional[int],  Field(default=None,gt=0,lt=120, description="Age of the patient")]
    gender: Annotated[Optional[Literal["male","female"]],  Field(default=None,description="Gender of the patient")]
    height: Annotated[Optional[float],  Field(default=None,gt=0,description="Height of the patient in meters")]
    weight: Annotated[Optional[float],  Field(default=None,gt=0,description="Weight of the patient in kilograms")]


@app.put("/edit/{patient_id}")
def update_patient(patient_id:str ,patient_update:UpdatePatient):
    data = load_data()
    # Validation
    if patient_id not in data:
        raise HTTPException(status_code = 404 , detail ="Patient not found")
    
    existing_patient_info=data[patient_id] 
    updated_patient_info = patient_update.model_dump(exclude_unset=True) # It exclude the Values which have NONE.
    print("updated_patient_info : ", updated_patient_info)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value
    # This existing_patient_info was updated now.
    data[patient_id] = existing_patient_info
    existing_patient_info['id'] = patient_id # existing_patient_info don't have id.
    patient_pydantic_object = Patient(**existing_patient_info)
    existing_patient_info = patient_pydantic_object.model_dump(exclude='id')
    # Add this dict to data
    data[patient_id] = existing_patient_info

    with open("patient.json",'w') as f:
        json.dump(data,f)
    return JSONResponse(
        status_code = 200,
        content = {"message" : "Patient Updated" ,
                    "data" : data[patient_id]}
    )

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):
    # load_data
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail = "Patient not found.")
    # Delete that patient if from data
    del data[patient_id]

    with open("patient.json" , 'w') as f:
        json.dump(data,f)
    
    return JSONResponse(
        status_code=200,
        content = {"message" : "patient deleted"}
    )