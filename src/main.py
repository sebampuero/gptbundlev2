from fastapi import FastAPI
from fastapi.routing import APIRoute

from src.common.config import settings
from src.common.logging import setup_logging 
from src.routers import api_router


setup_logging(level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT, date_format=settings.LOG_DATE_FORMAT)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(api_router, prefix=settings.API_V1_STR)
