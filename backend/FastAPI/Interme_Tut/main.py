from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.logging import setup_logging, get_logger
import logging
import uvicorn
from routes import user_auth_r , me_r

# Initialize logging
setup_logging()
# Get loggers
logger = get_logger()                  # mainLogger
module_logger = logging.getLogger(__name__)  # module-based logger

def create_app():
    "Application factory - easier to testing and scaling."
    app = FastAPI(
        title = "FastAPI Boilerplate",
        version = "1.0.0",
        description = "FastAPI Boilerplate for API development"
    )
    # ----------------- Middleware -------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins = ["*"],
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"],
    )
    # ----------------- Routers -----------------------
    app.include_router(user_auth_r)
    app.include_router(me_r)

    @app.get("/")
    async def roots():
        logger.info("Root")
        return {"message" : "Creating logging system. . ."} 
    
    return app 

app = create_app() 

if __name__ == "__main__":
    print("Starting Server. . .")
    logger.info("Starting Server. . .") 
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True) 