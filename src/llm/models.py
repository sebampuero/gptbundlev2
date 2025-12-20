from typing import List, Dict, Any
from pydantic import BaseModel


class BaseMessage(BaseModel):
    role: str
    llm_model: str

class MessageText(BaseMessage):
    content: str

class MessageImage(BaseMessage):
    content: List[Dict[str, Any]] # contains two objects with type either text or image_url

class Chat(BaseModel):
    messages: List[MessageText | MessageImage]