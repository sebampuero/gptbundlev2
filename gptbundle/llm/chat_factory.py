from typing import Any

from .models import Chat, MessageText


def convert_chat_to_model(chat: dict[str, Any]) -> Chat:
    messages = []
    for message in chat["messages"]:
        if message["message_type"] == "text":
            messages.append(
                MessageText(
                    role=message["role"],
                    content=message["content"],
                    llm_model=message["llm_model"],
                )
            )
        elif message["message_type"] == "image":
            # process image (TODO for later)
            pass
    return Chat(messages=messages)
