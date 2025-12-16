from fastapi import APIRouter

from src.user.router import router as user_router
from src.messaging.router import router as messaging_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(messaging_router, prefix="/messaging", tags=["messaging"])
