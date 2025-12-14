from .models import Chat as ChatModel
from .schemas import ChatCreate


class ChatRepository:
    def create_chat(self, chat_in: ChatCreate) -> ChatModel:
        pass

    def get_chat(self, chat_id: str) -> ChatModel | None:
        pass
