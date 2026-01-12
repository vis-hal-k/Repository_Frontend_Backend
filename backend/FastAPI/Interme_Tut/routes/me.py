from datetime import timedelta
from fastapi import APIRouter, HTTPException , status , Depends 
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import text 
from pydantic import BaseModel 
from datetime import datetime
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext 
from db import get_db
from .user_auth import Current_User

me_r = APIRouter(prefix="/Bearer" , tags = ["Bearer"])
@me_r.get("/me")
async def get_current_user_info(current_user : Current_User):
    """
    Protected route example - requires valid accesss token.
    """ 
    return { 
        "user_id" : current_user["id"] ,
        "username" : current_user["username"] ,
        "email" : current_user["email"] ,
        "is_active" : current_user["is_active"]
    }
    