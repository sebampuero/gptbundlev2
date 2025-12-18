from typing import List
import uuid
import time
from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    text: str
    type: str
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
