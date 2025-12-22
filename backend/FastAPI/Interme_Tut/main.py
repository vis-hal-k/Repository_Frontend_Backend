from fastapi import FastAPI
from core.logging import setup_logging, get_logger
import logging

# Initialize logging
setup_logging()

# Get loggers
app_logger = get_logger()                  # mainLogger
module_logger = logging.getLogger(__name__)  # module-based logger

app = FastAPI()


@app.get("/health")
def health_check():
    app_logger.debug("DEBUG: Health check triggered (mainLogger)")
    app_logger.info("INFO: Health check triggered (mainLogger)")
    module_logger.info("INFO: Health check triggered (module logger)")
    return {"status": "ok"}
