# ==========================================================
# LOGGING SETUP MODULE
# Responsible for initializing application-wide logging
# using a YAML-based logging configuration.
#
# This module should be imported and setup_logging()
# should be called ONCE during application startup.
# ==========================================================

import logging # Core Python logging module used to create and emit log records
import logging.config # Provides dictConfig() which loads logging configuration from a dictionary
import yaml # Used to parse YAML configuration files (logger_config.yaml)
from pathlib import Path
# Pathlib provides OS-independent path handling
# Safer and cleaner than using raw string paths

# ----------------------------------------------------------
# setup_logging
# ----------------------------------------------------------
def setup_logging(config_path="core/logger_config.yaml"):
    # Initializes application logging configuration
    # This function:
    # - Loads logging configuration from a YAML file
    # - Applies it using logging.config.dictConfig()
    # - Falls back to basic logging if config file is missing
    # IMPORTANT:
    # This function MUST be called once during application startup
    # (e.g., inside main.py before any logs are emitted)

    logger_config_file = Path(config_path)
    # Convert provided path into a Path object
    # Allows existence check and cross-platform compatibility

    if logger_config_file.exists():
        # If logging configuration file exists

        with open(logger_config_file, "r") as f:
            # Open YAML configuration file in read mode

            logger_config = yaml.safe_load(f.read())
            # Parse YAML content into a Python dictionary
            # safe_load() prevents execution of arbitrary code

            logging.config.dictConfig(logger_config)
            # Apply logging configuration globally
            # This sets:
            # - formatters
            # - handlers
            # - loggers
            # - root logger
            # across the entire application

    else:
        # Fallback behavior if YAML config file is missing
        logging.basicConfig(level=logging.INFO)
        # Initialize default logging configuration
        # Logs will be sent to console with INFO level
        print("logging_config.yaml not found, using basic logging")
        # Print warning to notify developer
        # (print is acceptable here because logging is not yet configured)

# ----------------------------------------------------------
# get_logger
# ----------------------------------------------------------
def get_logger():
    # Returns a named application logger
    #
    # This logger corresponds to the custom logger defined in
    # logger_config.yaml under:
    #
    # loggers:
    #   mainLogger:
    #     level: DEBUG
    #
    # Usage:
    #   logger = get_logger()
    #   logger.info("Application started")
    #
    # Centralizing logger creation avoids:
    # - Hardcoded logger names across modules
    # - Inconsistent logging behavior

    return logging.getLogger("mainLogger")
    # Retrieve and return the configured logger instance
