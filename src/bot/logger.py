import logging
import sys
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logging(log_level=logging.INFO, verbose=False):
    log_dir = "logs"
    log_file = f"{log_dir}/bot.log"

    # Create log directory if it doesn't exist
    import os
    os.makedirs(log_dir, exist_ok=True)
    open(f"{log_dir}/.gitkeep", 'a').close()


    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    if verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)

    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)

    # Rotating File Handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)

    # Add handlers to the root logger
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    return root_logger
