import asyncio
import logging
from typing import Any

from gptbundle.media_storage.storage import delete_objects, generate_presigned_url

from .elasticsearch_repository import ElasticsearchRepository
from .repository import ChatRepository
from .schemas import Chat, ChatCreate, MessageCreate

logger = logging.getLogger(__name__)


async def create_chat(
    chat_in: ChatCreate,
    chat_repo: ChatRepository,
    es_repo: ElasticsearchRepository,
) -> Chat:
    chat = await asyncio.to_thread(chat_repo.create_chat, chat_in)
    await es_repo.store_chat(chat)
    return chat


async def get_chat(
    chat_id: str, timestamp: float, chat_repo: ChatRepository, user_email: str
) -> Chat | None:
    chat = await asyncio.to_thread(chat_repo.get_chat, chat_id, timestamp, user_email)
    if chat:
        for message in chat.messages:
            if message.media_s3_keys:
                message.presigned_urls = [
                    generate_presigned_url(key) for key in message.media_s3_keys
                ]
    return chat


async def get_chats_by_user_email_paginated(
    user_email: str,
    chat_repo: ChatRepository,
    limit: int | None = None,
    last_evaluated_key: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return await asyncio.to_thread(
        chat_repo.get_chats_by_user_email_paginated,
        user_email,
        limit=limit,
        last_evaluated_key=last_evaluated_key,
    )


async def get_chats_by_user_email(
    user_email: str,
    chat_repo: ChatRepository,
) -> list[Chat]:
    return await asyncio.to_thread(chat_repo.get_chats_by_user_email, user_email)


async def append_messages(
    chat_id: str,
    timestamp: float,
    messages: list[MessageCreate],
    chat_repo: ChatRepository,
    user_email: str,
    es_repo: ElasticsearchRepository,
) -> bool:
    success = await asyncio.to_thread(
        chat_repo.append_messages, chat_id, timestamp, messages, user_email
    )
    if success:
        full_chat = await asyncio.to_thread(
            chat_repo.get_chat, chat_id, timestamp, user_email
        )
        if full_chat:
            await es_repo.update_chat(full_chat)
    return success


async def delete_chat(
    chat_id: str,
    timestamp: float,
    chat_repo: ChatRepository,
    user_email: str,
    es_repo: ElasticsearchRepository,
) -> bool:
    chat = await asyncio.to_thread(chat_repo.get_chat, chat_id, timestamp, user_email)
    if not chat:
        return False

    s3_keys = []
    for msg in chat.messages:
        if msg.media_s3_keys:
            s3_keys.extend(msg.media_s3_keys)

    deleted = await asyncio.to_thread(
        chat_repo.delete_chat, chat_id, timestamp, user_email
    )
    if deleted:
        if s3_keys:
            delete_objects(s3_keys)
        await es_repo.delete_chat(chat_id)

    return deleted
