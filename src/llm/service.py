from litellm import acompletion
from .models import Chat
from typing import Dict, Any
from .chat_factory import convert_chat_to_model
from typing import AsyncGenerator

async def generate_text_response(chat: Dict[str, Any]) -> AsyncGenerator[str, None]:
    chat = convert_chat_to_model(chat)
    llm_model = chat.messages[-1].llm_model
    return await acompletion(model=llm_model, messages=[m.model_dump() for m in chat.messages], stream=True)

async def generate_image_response(chat: Dict[str, Any]) -> AsyncGenerator[str, None]:
    # TODO: implement. This function generates images from user prompts. We can call the Sora API.
    pass