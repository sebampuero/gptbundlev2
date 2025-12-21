import logging
import sys
from datetime import datetime


def setup_logging(level: int, log_format: str, date_format: str):

    formatter = logging.Formatter(log_format, datefmt=date_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = []
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)