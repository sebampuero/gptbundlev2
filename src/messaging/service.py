from .repository import ChatRepository
from .schemas import ChatCreate, Chat
from typing import List

def create_chat(chat_in: ChatCreate, chat_repo: ChatRepository) -> Chat:
    return chat_repo.create_chat(chat_in)

def get_chat(chat_id: str, timestamp: float, chat_repo: ChatRepository) -> Chat | None:
    return chat_repo.get_chat(chat_id, timestamp)

def get_chats_by_user_email(user_email: str, chat_repo: ChatRepository) -> list[Chat]:
    return chat_repo.get_chats_by_user_email(user_email)

def append_messages(chat_id: str, timestamp: float, messages: List[MessageCreate], chat_repo: ChatRepository) -> bool:
    return chat_repo.append_messages(chat_id, timestamp, messages)