from datetime import datetime

import pytest

from gptbundle.messaging.schemas import Chat, MessageCreate, MessageRole


@pytest.mark.asyncio
async def test_store_and_search_chat(es_repo, cleanup_es: list):
    chat_id = "test_es_search_id"
    user_email = "es_test@example.com"
    timestamp = datetime.now().timestamp()

    chat = Chat(
        chat_id=chat_id,
        user_email=user_email,
        timestamp=timestamp,
        messages=[
            MessageCreate(
                content="This is a unique keyword for searching",
                role=MessageRole.USER,
                message_type="text",
                llm_model="gpt4",
            )
        ],
    )

    await es_repo.store_chat(chat)
    cleanup_es.append(chat_id)

    # Search for the chat
    results = await es_repo.search_chats(user_email, "unique keyword")
    assert len(results) > 0
    assert results[0].chat_id == chat_id
    assert results[0].user_email == user_email


@pytest.mark.asyncio
async def test_search_chats_filtering(es_repo, cleanup_es: list):
    user1 = "user1@example.com"
    user2 = "user2@example.com"
    keyword = "sharedcontent"

    chat1 = Chat(
        chat_id="chat_user1",
        user_email=user1,
        timestamp=datetime.now().timestamp(),
        messages=[
            MessageCreate(
                content=keyword,
                role=MessageRole.USER,
                message_type="text",
                llm_model="gpt4",
            )
        ],
    )
    chat2 = Chat(
        chat_id="chat_user2",
        user_email=user2,
        timestamp=datetime.now().timestamp() + 1,
        messages=[
            MessageCreate(
                content=keyword,
                role=MessageRole.USER,
                message_type="text",
                llm_model="gpt4",
            )
        ],
    )

    await es_repo.store_chat(chat1)
    await es_repo.store_chat(chat2)
    cleanup_es.append(chat1.chat_id)
    cleanup_es.append(chat2.chat_id)

    # User 1 should only see their chat
    results1 = await es_repo.search_chats(user1, keyword)
    assert len(results1) == 1
    assert results1[0].user_email == user1

    # User 2 should only see their chat
    results2 = await es_repo.search_chats(user2, keyword)
    assert len(results2) == 1
    assert results2[0].user_email == user2


@pytest.mark.asyncio
async def test_delete_from_es(es_repo, cleanup_es: list):
    chat_id = "to_be_deleted_from_es"
    user_email = "delete_test@example.com"

    chat = Chat(
        chat_id=chat_id,
        user_email=user_email,
        timestamp=datetime.now().timestamp(),
        messages=[
            MessageCreate(
                content="delete me",
                role=MessageRole.USER,
                message_type="text",
                llm_model="gpt4",
            )
        ],
    )

    await es_repo.store_chat(chat)
    # We'll manually delete, but cleanup_es is a safety net
    cleanup_es.append(chat_id)

    # Verify it exists
    results = await es_repo.search_chats(user_email, "delete")
    assert len(results) == 1

    # Delete it
    await es_repo.delete_chat(chat_id)

    # Verify it's gone
    results_after = await es_repo.search_chats(user_email, "delete")
    assert len(results_after) == 0
