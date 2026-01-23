import asyncio
import base64
import uuid
from collections.abc import AsyncGenerator

from litellm import acompletion

from gptbundle.media_storage.storage import generate_presigned_url, upload_file
from gptbundle.messaging.schemas import Chat as MessagingChat
from gptbundle.messaging.schemas import MessageCreate, MessageRole

from .chat_factory import convert_chat_to_model


async def generate_text_response(chat: MessagingChat) -> AsyncGenerator[str, None]:
    chat = convert_chat_to_model(chat)
    llm_model = chat.messages[-1].llm_model
    return await acompletion(
        model=llm_model, messages=[m.model_dump() for m in chat.messages], stream=True
    )


async def generate_image_response(user_message: MessageCreate) -> MessageCreate:
    if user_message.message_type != "image":
        raise ValueError(
            "Chat message type must be 'image' to generate an image response"
        )
    response = await acompletion(
        model=user_message.llm_model, messages=[user_message.model_dump()]
    )
    text_response = response.choices[0].message.content
    images = response.choices[0].message.images
    s3_keys = []
    presigned_urls = []
    for image in images:
        if image.get("type") == "image_url":
            _, encoded = image.get("image_url").get("url").split(",", 1)
            image_bytes = base64.b64decode(encoded)
            s3_key = f"permanent/{str(uuid.uuid4())}.png"
            await asyncio.to_thread(upload_file, image_bytes, s3_key)
            s3_keys.append(s3_key)
            presigned_urls.append(generate_presigned_url(s3_key))
    return MessageCreate(
        content=text_response,
        role=MessageRole.ASSISTANT,
        message_type="text",
        media_s3_keys=s3_keys,
        presigned_urls=presigned_urls,
        llm_model=user_message.llm_model,
    )
