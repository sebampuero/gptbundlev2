import asyncio
import base64
import logging
import uuid
from collections.abc import AsyncGenerator

import litellm
from litellm import acompletion

from gptbundle.common.config import settings
from gptbundle.llm.exceptions import ModelDoesNotSupportReasoningEffortError
from gptbundle.media_storage.storage import generate_presigned_url, upload_file
from gptbundle.messaging.schemas import MessageCreate, MessageRole

from .chain_router import router
from .chat_factory import input_to_llm

logger = logging.getLogger(__name__)


async def generate_text_response(
    user_message: MessageCreate,
    chat_id: str,
) -> AsyncGenerator[str, None]:
    formatted_input = input_to_llm(user_message)
    use_rag = bool(user_message.pdf_s3_keys)
    logger.debug(f"Using reasoning_effort: {user_message.reasoning_effort}")
    if user_message.reasoning_effort and not litellm.supports_reasoning(
        user_message.llm_model
    ):
        raise ModelDoesNotSupportReasoningEffortError(
            f"Model {user_message.llm_model} does not support reasoning effort"
        )
    chain = router.route(
        use_rag=use_rag,
        chat_id=chat_id,
        llm_model=user_message.llm_model,
        reasoning_effort=user_message.reasoning_effort,
    )
    async for token in chain.astream(
        formatted_input, config={"configurable": {"session_id": chat_id}}
    ):
        yield token.content


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
    logger.debug(f"Generated images: {images}")
    for image in images:
        if image.get("type") == "image_url":
            _, encoded = image.get("image_url").get("url").split(",", 1)
            image_bytes = base64.b64decode(encoded)
            s3_key = f"{settings.S3_PERMANENT_PREFIX}{uuid.uuid4()}.png"
            await asyncio.to_thread(upload_file, image_bytes, s3_key)
            s3_keys.append(s3_key)
            presigned_urls.append(generate_presigned_url(s3_key))
    return MessageCreate(
        content=text_response,
        role=MessageRole.ASSISTANT,
        message_type="text",
        img_s3_keys=s3_keys,
        img_presigned_urls=presigned_urls,
        llm_model=user_message.llm_model,
    )
