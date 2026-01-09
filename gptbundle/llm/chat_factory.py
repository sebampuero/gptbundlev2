from gptbundle.media_storage.storage import generate_presigned_url
from gptbundle.messaging.schemas import Chat as MessagingChat

from .models import Chat, MessageImage, MessageText


def convert_chat_to_model(chat: MessagingChat) -> Chat:
    messages = []
    for message in chat.messages:
        if not message.media_s3_keys:
            messages.append(
                MessageText(
                    role=message.role,
                    content=message.content,
                    llm_model=message.llm_model,
                )
            )
        else:
            image_content = [{"type": "text", "text": message.content}]
            for key in message.media_s3_keys:
                presigned_url = generate_presigned_url(key)
                image_content.append(
                    {"type": "image_url", "image_url": {"url": presigned_url}}
                )
            messages.append(
                MessageImage(
                    role=message.role,
                    content=image_content,
                    llm_model=message.llm_model,
                )
            )
    return Chat(messages=messages)
