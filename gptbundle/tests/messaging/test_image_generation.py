from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from gptbundle.common.config import settings
from gptbundle.messaging.schemas import MessageCreate, MessageRole
from gptbundle.security.service import generate_access_token


@pytest.fixture
def mock_generate_image_response():
    with patch(
        "gptbundle.messaging.router.generate_image_response", new_callable=AsyncMock
    ) as mock:
        yield mock


@pytest.fixture
def mock_generate_presigned_url():
    with patch("gptbundle.messaging.service.generate_presigned_url") as mock:
        mock.return_value = "https://example.com/presigned_url"
        yield mock


def test_image_generation_returns_presigned_urls(
    client: TestClient,
    mock_generate_image_response,
    mock_generate_presigned_url,
    cleanup_chats: list,
    es_repo,
    cleanup_es: list,
):
    user_email = "test_image_gen@example.com"
    token = generate_access_token(user_email)

    # Mock the LLM response to return a message with S3 keys
    s3_key = "permanent/test_image.png"
    mock_response_message = MessageCreate(
        content="Here is an image",
        role=MessageRole.ASSISTANT,
        message_type="text",
        media_s3_keys=[s3_key],
        llm_model="test-model",
    )
    mock_generate_image_response.return_value = mock_response_message

    payload = {
        "content": "Generate an image",
        "role": MessageRole.USER,
        "message_type": "image",
        "llm_model": "test-model",
    }

    # Call the endpoint
    # Note: Using chat_id="new" and timestamp=0 to create a new chat
    response = client.post(
        f"{settings.API_V1_STR}/messaging/image_generation?chat_id=new&chat_timestamp=0",
        json=payload,
        cookies={"access_token": token},
    )

    assert response.status_code == 200
    chat = response.json()

    # Cleanup
    cleanup_chats.append((chat["chat_id"], chat["timestamp"]))
    cleanup_es.append(chat["chat_id"])

    # Verify the response contains the assistant message
    messages = chat["messages"]
    assert len(messages) >= 2  # User message + Assistant message
    assistant_message = messages[-1]

    assert assistant_message["role"] == "assistant"
    assert assistant_message["media_s3_keys"] == [s3_key]

    # This assertion is expected to fail before the fix
    assert assistant_message["presigned_urls"] is not None
    assert len(assistant_message["presigned_urls"]) == 1
    assert assistant_message["presigned_urls"][0] == "https://example.com/presigned_url"
