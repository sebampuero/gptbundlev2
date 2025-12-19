from models import Chat

def convert_chat_to_model(chat: Dict[str, Any]) -> Chat:
    messages = []
    for message in chat["messages"]:
        if message["media"]:
            # process media (TODO for later)
            pass
        else:
            messages.append(MessageText(role=message["role"], content=message["content"]))
    return Chat(messages=messages)