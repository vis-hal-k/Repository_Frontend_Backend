from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from core import settings 
from typing import Generator
from core import get_logger 

logger = get_logger() 

engine = create_engine(settings.DATABASE_URL, echo=True , future = True) 
SessionLocal = sessionmaker(autocommit = False , autoflush = False, bind = engine , future = True) 
Base = declarative_base() 

def get_db():
    """ This use only in FastAPI endpoints:
    def endpoint(db: Session = Depends(get_db)):
    It yields a session and ensures it is closed afterwards.
    We cannot directly call get_db().
    """
    db = SessionLocal() 
    try:
        yield db 
    finally:
        db.close() 
