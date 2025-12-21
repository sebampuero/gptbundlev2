from fastapi import APIRouter

from gptbundle.messaging.router import router as messaging_router
from gptbundle.user.router import router as user_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(messaging_router, prefix="/messaging", tags=["messaging"])
