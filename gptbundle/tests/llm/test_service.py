import base64
from unittest.mock import AsyncMock, Mock, patch

import pytest

from gptbundle.llm.service import generate_image_response
from gptbundle.messaging.schemas import MessageCreate, MessageRole


@pytest.mark.asyncio
async def test_generate_image_response_success():
    # Mock data
    user_message = MessageCreate(
        content="Draw a cat",
        role=MessageRole.USER,
        message_type="image",
        llm_model="dall-e-3",
    )

    mock_image_bytes = b"fake_image_data"
    mock_b64_image = base64.b64encode(mock_image_bytes).decode("utf-8")
    mock_image_url = f"data:image/png;base64,{mock_b64_image}"

    # Mock litellm response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Here is your image"
    mock_image_dict = {
        "type": "image_url",
        "image_url": {"url": mock_image_url},
    }
    mock_response.choices[0].message.images = [mock_image_dict]

    # Mock dependencies
    with (
        patch(
            "gptbundle.llm.service.acompletion", new_callable=AsyncMock
        ) as mock_acompletion,
        patch("gptbundle.llm.service.upload_file") as mock_upload_file,
        patch(
            "gptbundle.llm.service.generate_presigned_url"
        ) as mock_generate_presigned_url,
    ):
        mock_acompletion.return_value = mock_response
        mock_generate_presigned_url.side_effect = (
            lambda key: f"https://s3.example.com/{key}"
        )

        # Execute
        result = await generate_image_response(user_message)

        # Verify
        assert result.role == MessageRole.ASSISTANT
        assert result.content == "Here is your image"
        assert result.message_type == "text"
        assert len(result.media_s3_keys) == 1
        assert len(result.presigned_urls) == 1
        assert result.media_s3_keys[0].startswith("permanent/")
        assert result.media_s3_keys[0].endswith(".png")
        assert (
            f"https://s3.example.com/{result.media_s3_keys[0]}"
            == result.presigned_urls[0]
        )

        # Verify mocks called
        mock_acompletion.assert_called_once()
        mock_upload_file.assert_called_once()
        # upload_file takes (file_obj, key), check first arg is bytes
        args, _ = mock_upload_file.call_args
        assert args[0] == mock_image_bytes
        assert args[1] == result.media_s3_keys[0]


@pytest.mark.asyncio
async def test_generate_image_response_invalid_type():
    user_message = MessageCreate(
        content="Just text",
        role=MessageRole.USER,
        message_type="text",  # Invalid for this function
        llm_model="gpt-4",
    )

    with pytest.raises(ValueError, match="Chat message type must be 'image'"):
        await generate_image_response(user_message)
