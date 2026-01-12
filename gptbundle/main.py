from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    root_path=settings.SUBDIRECTORY,
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
