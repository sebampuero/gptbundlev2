import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from gptbundle.common.config import settings
from gptbundle.messaging.schemas import (
    MessageRole,
    WebSocketMessage,
    WebSocketMessageType,
)
from gptbundle.security.service import generate_access_token


def is_valid_uuid4(uuid_string: str) -> bool:
    try:
        uuid_obj = uuid.UUID(uuid_string)
        return uuid_obj.version == 4
    except ValueError:
        return False


def test_websocket_combined(
    sync_client, sync_cleanup_chats: list, sync_es_repo, sync_cleanup_es: list
):
    """
    Combined WebSocket tests to avoid loop closure issues between tests.
    """
    token = generate_access_token("test@email.com")

    mock_chunk = AsyncMock()
    mock_chunk.choices = [AsyncMock()]
    mock_chunk.choices[0].delta.content = "I am a test model!"

    async def mock_gen(*args, **kwargs):
        async def inner():
            yield mock_chunk

        return inner()

    with patch(
        "gptbundle.messaging.router.generate_text_response", side_effect=mock_gen
    ):
        # 1. Test first connection
        chat_id_1 = str(uuid.uuid4())
        timestamp_1 = datetime.now().timestamp()
        payload_1 = {
            "user_message": {
                "content": "Hello 1",
                "role": MessageRole.USER,
                "message_type": "text",
                "llm_model": "openrouter/mistralai/devstral-2512:free",
            },
            "user_email": "test@email.com",
            "chat_id": chat_id_1,
            "timestamp": timestamp_1,
        }

        with sync_client.websocket_connect(
            f"{settings.API_V1_STR}/messaging/chat/text_ws",
            cookies={"access_token": token},
        ) as websocket:
            websocket.send_json(payload_1)
            total_response = ""
            while True:
                message = websocket.receive_json()
                ws_msg: WebSocketMessage = WebSocketMessage.model_validate(message)

                if ws_msg.type == WebSocketMessageType.NEW_CHAT:
                    sync_cleanup_chats.append((ws_msg.chat_id, ws_msg.chat_timestamp))
                    sync_cleanup_es.append(ws_msg.chat_id)
                elif ws_msg.type == WebSocketMessageType.TOKEN:
                    total_response += ws_msg.content
                elif ws_msg.type == WebSocketMessageType.STREAM_FINISHED:
                    break
                elif ws_msg.type == WebSocketMessageType.ERROR:
                    pytest.fail(f"Websocket error: {ws_msg.content}")

            assert "I am a test model!" in total_response

        # 2. Test string timestamp
        chat_id_2 = str(uuid.uuid4())
        timestamp_2_str = str(datetime.now().timestamp())
        payload_2 = {
            "user_message": {
                "content": "Hello 2",
                "role": MessageRole.USER,
                "message_type": "text",
                "llm_model": "openrouter/mistralai/devstral-2512:free",
            },
            "chat_id": chat_id_2,
            "timestamp": timestamp_2_str,
        }

        with sync_client.websocket_connect(
            f"{settings.API_V1_STR}/messaging/chat/text_ws",
            cookies={"access_token": token},
        ) as websocket:
            websocket.send_json(payload_2)
            while True:
                message = websocket.receive_json()
                ws_msg: WebSocketMessage = WebSocketMessage.model_validate(message)
                if ws_msg.type == WebSocketMessageType.STREAM_FINISHED:
                    break
                elif ws_msg.type == WebSocketMessageType.ERROR:
                    pytest.fail(f"Websocket error: {ws_msg.content}")

        # Cleanup for second chat
        sync_cleanup_chats.append((chat_id_2, float(timestamp_2_str)))
        sync_cleanup_es.append(chat_id_2)
