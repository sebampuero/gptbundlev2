import logging
from typing import Any

from gptbundle.media_storage.storage import delete_objects, generate_presigned_url

from .elasticsearch_repository import ElasticsearchRepository
from .repository import ChatRepository
from .schemas import Chat, ChatCreate, MessageCreate

logger = logging.getLogger(__name__)


def create_chat(
    chat_in: ChatCreate,
    chat_repo: ChatRepository,
    es_repo: ElasticsearchRepository,
) -> Chat:
    chat = chat_repo.create_chat(chat_in)
    es_repo.store_chat(chat)
    return chat


def get_chat(
    chat_id: str, timestamp: float, chat_repo: ChatRepository, user_email: str
) -> Chat | None:
    chat = chat_repo.get_chat(chat_id, timestamp, user_email)
    if chat:
        for message in chat.messages:
            if message.media_s3_keys:
                message.presigned_urls = [
                    generate_presigned_url(key) for key in message.media_s3_keys
                ]
    return chat


def get_chats_by_user_email_paginated(
    user_email: str,
    chat_repo: ChatRepository,
    limit: int | None = None,
    last_evaluated_key: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return chat_repo.get_chats_by_user_email_paginated(
        user_email, limit=limit, last_evaluated_key=last_evaluated_key
    )


def get_chats_by_user_email(
    user_email: str,
    chat_repo: ChatRepository,
) -> list[Chat]:
    return chat_repo.get_chats_by_user_email(user_email)


def append_messages(
    chat_id: str,
    timestamp: float,
    messages: list[MessageCreate],
    chat_repo: ChatRepository,
    user_email: str,
    es_repo: ElasticsearchRepository,
) -> bool:
    success = chat_repo.append_messages(chat_id, timestamp, messages, user_email)
    if success:
        full_chat = chat_repo.get_chat(chat_id, timestamp, user_email)
        if full_chat:
            es_repo.update_chat(full_chat)
    return success


def delete_chat(
    chat_id: str,
    timestamp: float,
    chat_repo: ChatRepository,
    user_email: str,
    es_repo: ElasticsearchRepository,
) -> bool:
    chat = chat_repo.get_chat(chat_id, timestamp, user_email)
    if not chat:
        return False

    s3_keys = []
    for msg in chat.messages:
        if msg.media_s3_keys:
            s3_keys.extend(msg.media_s3_keys)

    deleted = chat_repo.delete_chat(chat_id, timestamp, user_email)
    if deleted:
        if s3_keys:
            delete_objects(s3_keys)
        es_repo.delete_chat(chat_id)

    return deleted
