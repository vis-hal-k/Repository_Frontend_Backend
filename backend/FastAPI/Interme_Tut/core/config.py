# env and setting (loads .env)
import os
from pathlib import Path
from dotenv import load_dotenv

# Project root = where main.py exits
BASE_DIR = Path(__file__).resolve().parent.parent 
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)  


class Settings:
    """Application configuration settings.
    All values are loaded from environment variables.
    """
    # Application
    ENV: str = os.getenv("ENV" , "development")

    # Security / JWT
    SECRET_KEY : str = os.getenv("SECRET_KEY" , "")
    ALGORITHM: str = os.getenv("ALGORITHM" , "HS256") 

    ACCESS_TOKEN_EXPIRE_MIN : int = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"),"15") 
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS" , "7")) 

    # Database
    DATABASE_URL : str = os.getenv("DATABASE_URL","")

# -------------------------------------------
# Validation
# -------------------------------------------
def validate(self):
    if not self.SECRET_KEY:
        raise ValueError("SECRET_KEY is not set in .env")
    if not self.DATABASE_URL:
        raise ValueError("DATABASE_URL. is not set in .env") 

# Singleton setting instance
