import uuid
from datetime import datetime
from unittest.mock import patch

import pytest

from gptbundle.messaging.repository import ChatRepository
from gptbundle.messaging.schemas import ChatCreate, MessageCreate, MessageRole
from gptbundle.messaging.service import (
    append_messages,
    create_chat,
    delete_chat,
    get_chat,
    get_chats_by_user_email_paginated,
)


@pytest.mark.asyncio
async def test_create_chat(cleanup_chats: list, es_repo, cleanup_es: list):
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

    chat = await create_chat(chat_in, chat_repo, es_repo)
    cleanup_chats.append((chat.chat_id, chat.timestamp))
    cleanup_es.append(chat.chat_id)

    assert chat.chat_id == chat_id
    assert chat.user_email == user_email
    assert len(chat.messages) == 1
    assert chat.messages[0].content == "Hello"
    assert chat.messages[0].role == MessageRole.ASSISTANT

    db_chat = await get_chat(chat_id, timestamp, chat_repo, user_email)
    assert db_chat is not None
    assert db_chat.chat_id == chat_id
    assert db_chat.user_email == user_email
    assert len(db_chat.messages) == 1
    assert db_chat.messages[0].content == "Hello"
    assert db_chat.messages[0].role == MessageRole.ASSISTANT


@pytest.mark.asyncio
async def test_create_chat_with_no_messages(
    cleanup_chats: list, es_repo, cleanup_es: list
):
    chat_repo = ChatRepository()

    chat_id = "test_chat_id"
    timestamp = datetime.now().timestamp()
    user_email = "test@example.com"
    messages = []

    chat_in = ChatCreate(
        chat_id=chat_id, timestamp=timestamp, user_email=user_email, messages=messages
    )

    chat = await create_chat(chat_in, chat_repo, es_repo)
    cleanup_chats.append((chat.chat_id, chat.timestamp))
    cleanup_es.append(chat.chat_id)

    assert chat.chat_id == chat_id
    assert chat.user_email == user_email
    assert len(chat.messages) == 0

    db_chat = await get_chat(chat_id, timestamp, chat_repo, user_email)
    assert db_chat is not None
    assert db_chat.chat_id == chat_id
    assert db_chat.user_email == user_email
    assert len(db_chat.messages) == 0


@pytest.mark.asyncio
async def test_get_chat(cleanup_chats: list, es_repo, cleanup_es: list):
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

    chat = await create_chat(chat_in, chat_repo, es_repo)
    cleanup_chats.append((chat.chat_id, chat.timestamp))
    cleanup_es.append(chat.chat_id)

    found_chat = await get_chat(chat_id, timestamp, chat_repo, user_email)
    assert found_chat is not None
    assert found_chat.chat_id == chat_id

    not_found = await get_chat("nonexistent_id", timestamp, chat_repo, user_email)
    assert not_found is None


@pytest.mark.asyncio
async def test_get_chats_by_useremail_paginated(
    cleanup_chats: list, es_repo, cleanup_es: list
):
    chat_repo = ChatRepository()

    timestamp = datetime.now().timestamp()
    unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    user_email_1 = f"user1_{unique_suffix}@example.com"
    user_email_2 = f"user2_{unique_suffix}@example.com"

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
    await create_chat(chat_in_1, chat_repo, es_repo)
    cleanup_chats.append(("chat1", timestamp))
    cleanup_es.append("chat1")

    chat_in_2 = ChatCreate(
        chat_id="chat2",
        timestamp=timestamp + 1,
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
    await create_chat(chat_in_2, chat_repo, es_repo)
    cleanup_chats.append(("chat2", timestamp + 1))
    cleanup_es.append("chat2")

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
    await create_chat(chat_in_3, chat_repo, es_repo)
    cleanup_chats.append(("chat3", timestamp))
    cleanup_es.append("chat3")

    user1_response = await get_chats_by_user_email_paginated(user_email_1, chat_repo)
    user1_chats = user1_response["items"]
    assert len(user1_chats) == 2
    for chat in user1_chats:
        assert chat.user_email == user_email_1

    user2_response = await get_chats_by_user_email_paginated(user_email_2, chat_repo)
    user2_chats = user2_response["items"]
    assert len(user2_chats) == 1
    assert user2_chats[0].user_email == user_email_2

    empty_response = await get_chats_by_user_email_paginated(
        "nonexistent@example.com", chat_repo
    )
    assert len(empty_response["items"]) == 0


@pytest.mark.asyncio
async def test_get_chats_paginated_multi_page(
    cleanup_chats: list, es_repo, cleanup_es: list
):
    chat_repo = ChatRepository()

    timestamp = datetime.now().timestamp()
    user_email_1 = f"user_multi_{uuid.uuid4().hex[:8]}@example.com"

    # Create 5 chats for user 1
    for i in range(5):
        chat_id = f"multi_chat_{i}"
        chat_in = ChatCreate(
            chat_id=chat_id,
            timestamp=timestamp + i,
            user_email=user_email_1,
            messages=[
                MessageCreate(
                    content=f"Hello {i}",
                    role=MessageRole.ASSISTANT,
                    message_type="text",
                    llm_model="gpt4",
                )
            ],
        )
        await create_chat(chat_in, chat_repo, es_repo)
        cleanup_chats.append((chat_id, timestamp + i))
        cleanup_es.append(chat_id)

    # Test pagination with limit 2
    response1 = await get_chats_by_user_email_paginated(
        user_email_1, chat_repo, limit=2
    )
    assert len(response1["items"]) == 2
    assert response1["last_eval_key"] is not None

    # Test second page
    response2 = await get_chats_by_user_email_paginated(
        user_email_1, chat_repo, limit=2, last_evaluated_key=response1["last_eval_key"]
    )
    assert len(response2["items"]) == 2
    assert response2["last_eval_key"] is not None

    # Check that they are different
    chat_ids_1 = {c.chat_id for c in response1["items"]}
    chat_ids_2 = {c.chat_id for c in response2["items"]}
    assert chat_ids_1.isdisjoint(chat_ids_2)

    # Test third page (last item)
    response3 = await get_chats_by_user_email_paginated(
        user_email_1, chat_repo, limit=2, last_evaluated_key=response2["last_eval_key"]
    )
    assert len(response3["items"]) == 1
    assert response3["last_eval_key"] is None


@pytest.mark.asyncio
async def test_append_messages(cleanup_chats: list, es_repo, cleanup_es: list):
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

    chat = await create_chat(chat_in, chat_repo, es_repo)
    cleanup_chats.append((chat.chat_id, chat.timestamp))
    cleanup_es.append(chat.chat_id)

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

    updated_chat = await append_messages(
        chat_id, timestamp, new_messages, chat_repo, user_email, es_repo
    )
    assert updated_chat


@pytest.mark.asyncio
async def test_delete_chat(cleanup_chats: list, es_repo, cleanup_es: list):
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

    await create_chat(chat_in, chat_repo, es_repo)
    cleanup_es.append(chat_id)
    # No need to add to cleanup_chats since we're deleting it

    # Verify the chat exists
    found_chat = await get_chat(chat_id, timestamp, chat_repo, user_email)
    assert found_chat is not None

    # Delete the chat
    deleted = await delete_chat(chat_id, timestamp, chat_repo, user_email, es_repo)
    assert deleted is True

    # Verify the chat no longer exists
    deleted_chat = await get_chat(chat_id, timestamp, chat_repo, user_email)
    assert deleted_chat is None

    # Deleting a non-existent chat should return False
    deleted_again = await delete_chat(
        chat_id, timestamp, chat_repo, user_email, es_repo
    )
    assert deleted_again is False

    # Deleting with wrong chat_id should return False
    deleted_wrong_id = await delete_chat(
        "nonexistent_id", timestamp, chat_repo, user_email, es_repo
    )
    assert deleted_wrong_id is False


@pytest.mark.asyncio
async def test_delete_chat_with_s3_objects(
    cleanup_chats: list, es_repo, cleanup_es: list
):
    chat_repo = ChatRepository()
    chat_id = "test_s3_delete_chat_id"
    timestamp = datetime.now().timestamp()
    user_email = "test_s3@example.com"
    s3_keys = ["key1", "key2"]

    messages = [
        MessageCreate(
            content="Hello with images",
            role=MessageRole.USER,
            message_type="image",
            media_s3_keys=s3_keys,
            llm_model="gpt4",
        )
    ]

    chat_in = ChatCreate(
        chat_id=chat_id, timestamp=timestamp, user_email=user_email, messages=messages
    )

    await create_chat(chat_in, chat_repo, es_repo)
    cleanup_es.append(chat_id)

    with patch("gptbundle.messaging.service.delete_objects") as mock_delete_objects:
        deleted = await delete_chat(chat_id, timestamp, chat_repo, user_email, es_repo)
        assert deleted is True
        mock_delete_objects.assert_called_once_with(s3_keys)

    # Verify the chat no longer exists
    deleted_chat = await get_chat(chat_id, timestamp, chat_repo, user_email)
    assert deleted_chat is None
