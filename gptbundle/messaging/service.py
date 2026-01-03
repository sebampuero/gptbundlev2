from typing import Any

from .repository import ChatRepository
from .schemas import Chat, ChatCreate, MessageCreate


def create_chat(chat_in: ChatCreate, chat_repo: ChatRepository) -> Chat:
    return chat_repo.create_chat(chat_in)


def get_chat(
    chat_id: str, timestamp: float, chat_repo: ChatRepository, user_email: str
) -> Chat | None:
    return chat_repo.get_chat(chat_id, timestamp, user_email)


def get_chats_by_user_email_paginated(
    user_email: str,
    chat_repo: ChatRepository,
    limit: int | None = None,
    last_evaluated_key: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return chat_repo.get_chats_by_user_email_paginated(
        user_email, limit=limit, last_evaluated_key=last_evaluated_key
    )


def append_messages(
    chat_id: str,
    timestamp: float,
    messages: list[MessageCreate],
    chat_repo: ChatRepository,
    user_email: str,
) -> bool:
    return chat_repo.append_messages(chat_id, timestamp, messages, user_email)


def delete_chat(
    chat_id: str, timestamp: float, chat_repo: ChatRepository, user_email: str
) -> bool:
    return chat_repo.delete_chat(chat_id, timestamp, user_email)
