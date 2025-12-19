from typing import List, Dict, Any
from pydantic import BaseModel


class Chat(BaseModel):
    messages: List[MessageText | MessageImage]

class BaseMessage(BaseModel):
    role: str

class MessageText(BaseMessage):
    content: str

class MessageImage(BaseMessage):
    content: List[Dict[str, Any]] # contains two objects with type either text or image_url

