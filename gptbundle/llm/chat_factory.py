from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from gptbundle.media_storage.storage import generate_presigned_url
from gptbundle.messaging.schemas import MessageCreate, MessageRole


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
    if message.img_presigned_urls:
        content = [{"type": "text", "text": message.content}]
        for url in message.img_presigned_urls:
            content.append({"type": "image_url", "image_url": {"url": url}})
    else:
        content = message.content

    if message.role == MessageRole.USER:
        return HumanMessage(content=content)
    elif message.role == MessageRole.ASSISTANT:
        return AIMessage(content=content)
    else:
        raise ValueError(f"Unsupported role: {message.role}")
