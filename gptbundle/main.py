from fastapi import FastAPI

from gptbundle.common.config import settings
from gptbundle.common.logging import setup_logging
from gptbundle.routers import api_router

setup_logging(
    root_level=settings.ROOT_LOG_LEVEL,
    app_level=settings.APP_LOG_LEVEL,
    log_format=settings.LOG_FORMAT,
    date_format=settings.LOG_DATE_FORMAT,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(api_router, prefix=settings.API_V1_STR)
