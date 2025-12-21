import logging
import sys

from .config import settings


def setup_logging(root_level: str, app_level: str, log_format: str, date_format: str):
    formatter = logging.Formatter(log_format, datefmt=date_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(root_level)

    root_logger.handlers = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    my_app_logger = logging.getLogger(settings.PROJECT_NAME)
    my_app_logger.setLevel(app_level)
