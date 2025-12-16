from datetime import datetime
import pytest
from src.messaging.service import create_chat, get_chat, get_chats_by_user_email
from src.messaging.schemas import ChatCreate, MessageCreate
from src.messaging.repository import ChatRepository

def test_create_chat(cleanup_chats: list):
    chat_repo = ChatRepository()
    
    chat_id = "test_chat_id"
    timestamp = datetime.now().timestamp()
    user_email = "test@example.com"
    messages = [MessageCreate(text="Hello", type="AI")]
    
    chat_in = ChatCreate(
        chat_id=chat_id,
        timestamp=timestamp,
        user_email=user_email,
        messages=messages
    )
    
    chat = create_chat(chat_in, chat_repo)
    cleanup_chats.append((chat.chat_id, chat.timestamp))
    
    assert chat.chat_id == chat_id
    assert chat.user_email == user_email
    assert len(chat.messages) == 1
    assert chat.messages[0].text == "Hello"
    assert chat.messages[0].type == "AI"
    
    db_chat = get_chat(chat_id, timestamp, chat_repo)
    assert db_chat is not None
    assert db_chat.chat_id == chat_id
    assert db_chat.user_email == user_email
    assert len(db_chat.messages) == 1
    assert db_chat.messages[0].text == "Hello"
    assert db_chat.messages[0].type == "AI"
    
def test_get_chat(cleanup_chats: list):
    chat_repo = ChatRepository()
    
    chat_id = "test_get_chat_id"
    timestamp = datetime.now().timestamp()
    user_email = "test_get@example.com"
    messages = [MessageCreate(text="Hi", type="text")]
    
    chat_in = ChatCreate(
        chat_id=chat_id,
        timestamp=timestamp,
        user_email=user_email,
        messages=messages
    )
    
    chat = create_chat(chat_in, chat_repo)
    cleanup_chats.append((chat.chat_id, chat.timestamp))
    
    found_chat = get_chat(chat_id, timestamp, chat_repo)
    assert found_chat is not None
    assert found_chat.chat_id == chat_id
    
    not_found = get_chat("nonexistent_id", timestamp, chat_repo)
    assert not_found is None

def test_get_chats_by_useremail(cleanup_chats: list):
    chat_repo = ChatRepository()
    
    timestamp = datetime.now().timestamp()
    user_email_1 = "user1@example.com"
    user_email_2 = "user2@example.com"
    
    chat_in_1 = ChatCreate(
        chat_id="chat1",
        timestamp=timestamp,
        user_email=user_email_1,
        messages=[MessageCreate(text="Hello 1", type="text")]
    )
    create_chat(chat_in_1, chat_repo)
    cleanup_chats.append(("chat1", timestamp))
    
    chat_in_2 = ChatCreate(
        chat_id="chat2",
        timestamp=timestamp,
        user_email=user_email_1,
        messages=[MessageCreate(text="Hello 2", type="text")]
    )
    create_chat(chat_in_2, chat_repo)
    cleanup_chats.append(("chat2", timestamp))
    
    chat_in_3 = ChatCreate(
        chat_id="chat3",
        timestamp=timestamp,
        user_email=user_email_2,
        messages=[MessageCreate(text="Hello 3", type="text")]
    )
    create_chat(chat_in_3, chat_repo)
    cleanup_chats.append(("chat3", timestamp))
    
    user1_chats = get_chats_by_user_email(user_email_1, chat_repo)
    assert len(user1_chats) == 2
    for chat in user1_chats:
        assert chat.user_email == user_email_1

    user2_chats = get_chats_by_user_email(user_email_2, chat_repo)
    assert len(user2_chats) == 1
    assert user2_chats[0].user_email == user_email_2

    assert len(get_chats_by_user_email("nonexistent@example.com", chat_repo)) == 0