from fastapi import APIRouter, HTTPException , status , Depends 
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import text 
from pydantic import BaseModel 
from datetime import datetime , timedelta, timezone
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext 
from db import get_db
from core import settings
from jose import jwt, JWTError
import secrets 
import hashlib 
from core.logging import get_logger
logger = get_logger() 
# Add OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") 

def get_current_user(token: Annotated[str , Depends(oauth2_scheme)] , db: Session =Depends(get_db)):
    """
    Dependency to verify JWT token and get current user.
    Use this as a dependency in protected routes.
    """
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials" ,
        headers={"WWW-Authenticate" : "Bearer"},
    )
  
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM] 
        )
        username: str = payload.get("sub") 
        user_id : int = payload.get("user_id") 
        if username is None or user_id is None:
            raise credentials_exception
 
    except JWTError:
        raise credentials_exception
    
    obj = db.execute(text('''SELECT id, username, email, is_active FROM "public".users WHERE username=:username'''),{"username": username})
    user = obj.mappings().fetchone()
    if user is None:
        raise credentials_exception
    
    return dict(user)

Current_User = Annotated[dict , Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=["bcrypt"] , deprecated = 'auto')
class CreateUserRequest(BaseModel): 
    username : str 
    email : str 
    password : str

class Token(BaseModel):
    access_token : str
    token_type : str

class LoginRequest(BaseModel):
    username: str 
    password: str 

class RefreshTokenRequest(BaseModel):
    refresh_token: str 


def create_access_token(data:dict) -> str:
    to_encode = data.copy() 
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN)
    to_encode.update({"exp" : expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm = settings.ALGORITHM
    )

user_auth_r = APIRouter(prefix="/auth" , tags =["user_auth"]) 
@user_auth_r.post("/signup") 
async def signup(user_details : CreateUserRequest , db: Session=Depends(get_db)):
    params = {
        "email" : user_details.email ,
        "username" : user_details.username ,
        "hashed_password" : bcrypt_context.hash(user_details.password) ,
        "is_active" : True
    }
    create_query = text('''
                        CREATE TABLE IF NOT EXISTS "public".users(
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL ,
                        email VARCHAR(255) NOT NULL,
                        is_active VARCHAR(255) NOT NULL ,
                        refresh_token_hash TEXT NOT NULL ,
                        refresh_token_expires_at TIMESTAMP
                        )
                        ''')
    db.execute(create_query) 
    # INSERT 
    insert_query = text('''
                        INSERT INTO "public"."users" ("username" , "hashed_password" , "email" , "is_active")
                        VALUES (:username, :hashed_password , :email , :is_active)
                        RETURNING id ;
                        ''')
    result = db.execute(insert_query, params) 
    db.commit()
    return {"msg" : "Signup Successfully"} 


def authenticate_user(username: str , password : str , db) :
    obj = db.execute(text('''select id, username, hashed_password FROM "public".users WHERE username=:username''') , 
    {"username" : username}) 
    row_map = obj.mappings().fetchone()

    if row_map is None:
        return False, None
    
    res_dict = dict(row_map) 
    if not bcrypt_context.verify(password , res_dict['hashed_password']):
        return False, res_dict 
    return True , res_dict 

def create_refresh_token() -> str :
    return secrets.token_urlsafe(32)

def hash_refresh_token(token:str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def refresh_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


@user_auth_r.post("/login")
async def login(form_data: LoginRequest , db:Session=Depends(get_db)):
    username = form_data.username
    password = form_data.password
    user ,  user_dict = authenticate_user(username , password , db)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED , 
                                            detail = "Invalid username or password")

    # Create JWT token
    access_token = create_access_token(
        data = {
            "sub" : user_dict["username"],
            "user_id" : user_dict["id"]
        }
    )
    # Create Refresh Token (LONG-LIVED) 
    refresh_token = create_refresh_token()
    refresh_token_hash = hash_refresh_token(refresh_token) 
    ref_tok_exp = refresh_token_expiry()
    
    # Store refresh token in DB (mapped to USER)
    query = text('''UPDATE public.users SET refresh_token_hash=:hash,
                refresh_token_expires_at = :expiry 
                WHERE id = :user_id
         ''')
    db.execute( query , {"hash" : refresh_token_hash , 
                        "expiry" : ref_tok_exp ,
                        "user_id" : user_dict["id"] 
                        }
    ) 
    db.commit()

    return {
        "access_token" : access_token ,
        "refresh_token" : refresh_token ,
        "token_type" : "bearer"
    }


# Refresh Token. 
@user_auth_r.post("/refresh")
async def refresh_token(payload: RefreshTokenRequest , db : Session = Depends(get_db)):
    refresh_tok = payload.refresh_token 
    refresh_tok_hash = hash_refresh_token(refresh_tok) 
    # Find user by refresh token hash
    query = text(''' select id , username,  refresh_token_expires_at FROM public.users WHERE refresh_token_hash = :hash''')
    result = db.execute(query , {"hash" :refresh_tok_hash}) 
    user = result.mappings().fetchone() 
    if not user :
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED ,detail = "Invalid refresh token") 

    if user["refresh_token_expires_at"] < datetime.now(timezone.utc): 
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED , 
                                            detail = "Refresh token expiry") 

    # Create the new refresh token and stored in the DB.
    user_id  = user["id"] 
    new_access_token = create_access_token(
        data = {
            "sub" : user["username"],
            "user_id" : user["id"]
        }
    ) 
    new_refresh_token = create_refresh_token() 
    new_refresh_token_hash = hash_refresh_token(new_refresh_token) 
    new_expiry = refresh_token_expiry() 
    query = text('''UPDATE public.users SET 
                    refresh_token_hash = :hash,
                    refresh_token_expires_at = :expiry 
                    WHERE id = :id''')
    db.execute(query , {"hash" : new_refresh_token_hash ,
                        "expiry": new_expiry ,
                        "id" : user_id
                         }) 
    db.commit() 
    logger.info("Refresh token rotated for user_id = %s",user_id) 
    return {
        "access_token" : new_access_token ,
        "refresh_token" : new_refresh_token_hash
    }