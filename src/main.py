from fastapi import FastAPI
from fastapi.routing import APIRoute

from src.common.config import settings
from src.routers import api_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(api_router, prefix=settings.API_V1_STR)
