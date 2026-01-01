from fastapi import APIRouter

from gptbundle.llm.router import router as llm_router
from gptbundle.messaging.router import router as messaging_router
from gptbundle.security.router import router as security_router
from gptbundle.user.router import router as user_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(messaging_router, prefix="/messaging", tags=["messaging"])
api_router.include_router(llm_router, prefix="/llm", tags=["llm"])
api_router.include_router(security_router, prefix="/security", tags=["security"])
