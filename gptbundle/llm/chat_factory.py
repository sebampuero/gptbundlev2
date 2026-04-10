from typing import Any

from langchain_core.messages.base import BaseMessage

from gptbundle.media_storage.storage import generate_presigned_url
from gptbundle.messaging.schemas import MessageCreate


def input_to_llm(message: MessageCreate) -> dict[str, Any]:
    if not message.img_s3_keys:
        return {"question": message.content}

    question_content = [{"type": "text", "text": message.content}]
    for key in message.img_s3_keys:
        presigned_url = generate_presigned_url(key)
        question_content.append(
            {"type": "image_url", "image_url": {"url": presigned_url}}
        )

    return {"question": question_content}


def msg_schema_to_lc_base_message(message: MessageCreate) -> BaseMessage:
    # convert MessageCreate to LC BaseMessage
    pass
