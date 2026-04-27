from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from gptbundle.media_storage.storage import generate_presigned_url
from gptbundle.messaging.schemas import MessageCreate, MessageRole


def input_to_llm(message: MessageCreate) -> dict[str, Any]:
    if not message.img_s3_keys:
        return {"input": message.content}

    question_content = [{"type": "text", "text": message.content}]
    for key in message.img_s3_keys:
        presigned_url = generate_presigned_url(key)
        question_content.append(
            {"type": "image_url", "image_url": {"url": presigned_url}}
        )

    return {"input": question_content}


def msg_schema_to_lc_base_message(message: MessageCreate) -> BaseMessage:
    content: str | list[dict[str, Any]] = message.content

    image_urls = []
    if message.img_s3_keys:
        image_urls = [generate_presigned_url(key) for key in message.img_s3_keys]
    elif message.img_presigned_urls:
        image_urls = [
            url for url in message.img_presigned_urls if not url.startswith("blob:")
        ]

    if image_urls:
        content = [{"type": "text", "text": message.content}]
        for url in image_urls:
            content.append({"type": "image_url", "image_url": {"url": url}})

    if message.role == MessageRole.USER:
        return HumanMessage(content=content)
    elif message.role == MessageRole.ASSISTANT:
        return AIMessage(content=content)
    else:
        raise ValueError(f"Unsupported role: {message.role}")
