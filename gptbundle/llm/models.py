from typing import Any

from pydantic import BaseModel


class BaseMessage(BaseModel):
    role: str
    llm_model: str


class MessageText(BaseMessage):
    content: str


class MessageImage(BaseMessage):
    content: list[
        dict[str, Any]
    ]  # contains two objects with type either text or image_url


class Chat(BaseModel):
    messages: list[MessageText | MessageImage]
