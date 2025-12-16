from typing import Any, Annotated
from fastapi import Depends, APIRouter, HTTPException
from src.common.db import get_pg_db
from .service import create_chat, get_chat, get_chats_by_user_email
from .repository import ChatRepository
from .schemas import ChatCreate, Chat

router = APIRouter()

ChatRepositoryDep = Annotated[ChatRepository, Depends(ChatRepository)]


@router.post(
    "/chat",
    response_model=Chat
)
def new_chat(chat_repo: ChatRepositoryDep, chat_in: ChatCreate) -> Any:
    chat = create_chat(chat_repo=chat_repo, chat_in=chat_in)
    return chat


@router.get(
    "/chat/{chat_id}/{timestamp}",
    response_model=Chat,
    responses={
        404: {"description": "Chat not found"}
    },
)
def retrieve_chat(chat_repo: ChatRepositoryDep, chat_id: str, timestamp: float) -> Any:
    chat = get_chat(chat_repo=chat_repo, chat_id=chat_id, timestamp=timestamp)
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )
    return chat

@router.get(
    "/chats",
    response_model=list[Chat],
    responses={
        404: {"description": "Chats not found"}
    },
)
def retrieve_chats(chat_repo: ChatRepositoryDep, user_email: str) -> Any:
    chats = get_chats_by_user_email(chat_repo=chat_repo, user_email=user_email)
    if not chats:
        raise HTTPException(
            status_code=404,
            detail="Chats not found",
        )
    return chats
