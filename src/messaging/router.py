from typing import Any, Annotated, List
from fastapi import Depends, APIRouter, HTTPException
from src.common.db import get_pg_db
from .service import create_chat, get_chat, get_chats_by_user_email, append_messages, delete_chat
from .repository import ChatRepository
from .schemas import ChatCreate, Chat, MessageCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

ChatRepositoryDep = Annotated[ChatRepository, Depends(ChatRepository)]


@router.post(
    "/chat",
    response_model=Chat
)
def new_chat(chat_repo: ChatRepositoryDep, chat_in: ChatCreate) -> Any:
    logger.info(f"Received POST Request for new chat: {chat_in}")
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
    logger.info(f"Received GET Request for chat: {chat_id} and timestamp: {timestamp}")
    chat = get_chat(chat_repo=chat_repo, chat_id=chat_id, timestamp=timestamp)
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )
    return chat

@router.get(
    "/chats/{user_email}",
    response_model=list[Chat],
    responses={
        404: {"description": "Chats not found"}
    },
)
def retrieve_chats(chat_repo: ChatRepositoryDep, user_email: str) -> Any:
    logger.info(f"Received GET Request for chats of user: {user_email}")
    chats = get_chats_by_user_email(chat_repo=chat_repo, user_email=user_email)
    if not chats:
        raise HTTPException(
            status_code=404,
            detail="Chats not found",
        )
    return chats

@router.put(
    "/chat/{chat_id}/{timestamp}",
    responses={
        404: {"description": "Chat not found"}
    },
)
def chat_append_messages(
    chat_repo: ChatRepositoryDep, chat_id: str, timestamp: float, messages: List[MessageCreate]
) -> Any:
    # this appends messages to an existing chat. However, this doesn't scale very well
    # because it loads the entire chat into memory and updates for each new message, which doesn't
    # play well when there are thousands or millions of concurrent users.
    logger.info(f"Received PUT Request for chat: {chat_id} and timestamp: {timestamp} with {len(messages)} messages")
    chat = append_messages(chat_repo=chat_repo, chat_id=chat_id, timestamp=timestamp, messages=messages)
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )

@router.delete(
    "/chat/{chat_id}/{timestamp}",
    responses={
        404: {"description": "Chat not found"}
    },
)
def remove_chat(chat_repo: ChatRepositoryDep, chat_id: str, timestamp: float) -> Any:
    logger.info(f"Received DELETE Request for chat: {chat_id} and timestamp: {timestamp}")
    deleted = delete_chat(chat_repo=chat_repo, chat_id=chat_id, timestamp=timestamp)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )
