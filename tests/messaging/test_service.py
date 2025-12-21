from datetime import datetime

from gptbundle.messaging.repository import ChatRepository
from gptbundle.messaging.schemas import ChatCreate, MessageCreate, MessageRole
from gptbundle.messaging.service import (
    append_messages,
    create_chat,
    delete_chat,
    get_chat,
    get_chats_by_user_email,
)


def test_create_chat(cleanup_chats: list):
    chat_repo = ChatRepository()

    chat_id = "test_chat_id"
    timestamp = datetime.now().timestamp()
    user_email = "test@example.com"
    messages = [
        MessageCreate(
            content="Hello",
            role=MessageRole.ASSISTANT,
            message_type="text",
            llm_model="gpt4",
        )
    ]

    chat_in = ChatCreate(
        chat_id=chat_id, timestamp=timestamp, user_email=user_email, messages=messages
    )

    chat = create_chat(chat_in, chat_repo)
    cleanup_chats.append((chat.chat_id, chat.timestamp))

    assert chat.chat_id == chat_id
    assert chat.user_email == user_email
    assert len(chat.messages) == 1
    assert chat.messages[0].content == "Hello"
    assert chat.messages[0].role == MessageRole.ASSISTANT

    db_chat = get_chat(chat_id, timestamp, chat_repo)
    assert db_chat is not None
    assert db_chat.chat_id == chat_id
    assert db_chat.user_email == user_email
    assert len(db_chat.messages) == 1
    assert db_chat.messages[0].content == "Hello"
    assert db_chat.messages[0].role == MessageRole.ASSISTANT


def test_create_chat_with_no_messages(cleanup_chats: list):
    chat_repo = ChatRepository()

    chat_id = "test_chat_id"
    timestamp = datetime.now().timestamp()
    user_email = "test@example.com"
    messages = []

    chat_in = ChatCreate(
        chat_id=chat_id, timestamp=timestamp, user_email=user_email, messages=messages
    )

    chat = create_chat(chat_in, chat_repo)
    cleanup_chats.append((chat.chat_id, chat.timestamp))

    assert chat.chat_id == chat_id
    assert chat.user_email == user_email
    assert len(chat.messages) == 0

    db_chat = get_chat(chat_id, timestamp, chat_repo)
    assert db_chat is not None
    assert db_chat.chat_id == chat_id
    assert db_chat.user_email == user_email
    assert len(db_chat.messages) == 0


def test_get_chat(cleanup_chats: list):
    chat_repo = ChatRepository()

    chat_id = "test_get_chat_id"
    timestamp = datetime.now().timestamp()
    user_email = "test_get@example.com"
    messages = [
        MessageCreate(
            content="Hi",
            role=MessageRole.ASSISTANT,
            message_type="text",
            llm_model="gpt4",
        )
    ]

    chat_in = ChatCreate(
        chat_id=chat_id, timestamp=timestamp, user_email=user_email, messages=messages
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
        messages=[
            MessageCreate(
                content="Hello 1",
                role=MessageRole.ASSISTANT,
                message_type="text",
                llm_model="gpt4",
            )
        ],
    )
    create_chat(chat_in_1, chat_repo)
    cleanup_chats.append(("chat1", timestamp))

    chat_in_2 = ChatCreate(
        chat_id="chat2",
        timestamp=timestamp,
        user_email=user_email_1,
        messages=[
            MessageCreate(
                content="Hello 2",
                role=MessageRole.USER,
                message_type="text",
                llm_model="gpt4",
            )
        ],
    )
    create_chat(chat_in_2, chat_repo)
    cleanup_chats.append(("chat2", timestamp))

    chat_in_3 = ChatCreate(
        chat_id="chat3",
        timestamp=timestamp,
        user_email=user_email_2,
        messages=[
            MessageCreate(
                content="Hello 3",
                role=MessageRole.ASSISTANT,
                message_type="text",
                llm_model="gpt4",
            )
        ],
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


def test_append_messages(cleanup_chats: list):
    chat_repo = ChatRepository()

    chat_id = "test_append_messages_id"
    timestamp = datetime.now().timestamp()
    user_email = "test_append_messages@example.com"
    messages = [
        MessageCreate(
            content="Hello",
            role=MessageRole.ASSISTANT,
            message_type="text",
            llm_model="gpt4",
        )
    ]

    chat_in = ChatCreate(
        chat_id=chat_id, timestamp=timestamp, user_email=user_email, messages=messages
    )

    chat = create_chat(chat_in, chat_repo)
    cleanup_chats.append((chat.chat_id, chat.timestamp))

    new_messages = [
        MessageCreate(
            content="Hello 2",
            role=MessageRole.USER,
            message_type="text",
            llm_model="gpt4",
        ),
        MessageCreate(
            content="Hello 3",
            role=MessageRole.ASSISTANT,
            message_type="text",
            llm_model="gpt4",
        ),
    ]

    updated_chat = append_messages(chat_id, timestamp, new_messages, chat_repo)
    assert updated_chat


def test_delete_chat(cleanup_chats: list):
    chat_repo = ChatRepository()

    chat_id = "test_delete_chat_id"
    timestamp = datetime.now().timestamp()
    user_email = "test_delete@example.com"
    messages = [
        MessageCreate(
            content="Hello",
            role=MessageRole.ASSISTANT,
            message_type="text",
            llm_model="gpt4",
        )
    ]

    chat_in = ChatCreate(
        chat_id=chat_id, timestamp=timestamp, user_email=user_email, messages=messages
    )

    chat = create_chat(chat_in, chat_repo)
    # No need to add to cleanup_chats since we're deleting it

    # Verify the chat exists
    found_chat = get_chat(chat_id, timestamp, chat_repo)
    assert found_chat is not None

    # Delete the chat
    deleted = delete_chat(chat_id, timestamp, chat_repo)
    assert deleted is True

    # Verify the chat no longer exists
    deleted_chat = get_chat(chat_id, timestamp, chat_repo)
    assert deleted_chat is None

    # Deleting a non-existent chat should return False
    deleted_again = delete_chat(chat_id, timestamp, chat_repo)
    assert deleted_again is False

    # Deleting with wrong chat_id should return False
    deleted_wrong_id = delete_chat("nonexistent_id", timestamp, chat_repo)
    assert deleted_wrong_id is False
