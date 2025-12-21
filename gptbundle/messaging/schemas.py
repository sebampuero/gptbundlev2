from enum import Enum
from typing import List
import uuid
import time
from pydantic import BaseModel, ConfigDict, Field


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class WebSocketMessageType(str, Enum):
    NEW_CHAT = "chat_created"
    ERROR = "error"
    TOKEN = "token"
    STREAM_FINISHED = "stream_finished"

class MessageCreate(BaseModel):
    content: str
    role: MessageRole
    message_type: str = "text"
    media: str | None = None
    llm_model: str

class ChatBase(BaseModel):
    user_email: str
    messages: List[MessageCreate] = Field(default_factory=list)


class ChatCreate(ChatBase):
    chat_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=lambda: time.time())

class Chat(ChatCreate):
    model_config = ConfigDict(from_attributes=True)

class WebSocketMessage(BaseModel):
    type: WebSocketMessageType
    chat_id: str | None = None
    timestamp: float | None = None
    content: str | None = None
