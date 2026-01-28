import pytest
import respx
from fastapi import FastAPI
from httpx import Response

from gptbundle.common.config import settings
from gptbundle.llm.router import router


@pytest.fixture
async def client():
    from httpx import ASGITransport, AsyncClient

    app = FastAPI()
    app.include_router(router)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@respx.mock
@pytest.mark.asyncio
async def test_get_models(client):
    mock_response = {
        "data": [
            {
                "id": "google/gemma-3-12b-it:free",
                "description": "A very capable model.",
                "architecture": {
                    "modality": "text+image->text",
                    "input_modalities": ["text", "image"],
                    "output_modalities": ["text"],
                },
            },
            {
                "id": "openai/gpt-4o",
                "description": "The best model.",
                "architecture": {
                    "modality": "text->text",
                    "input_modalities": ["text"],
                    "output_modalities": ["text"],
                },
            },
        ]
    }

    respx.get(settings.OPENROUTER_MODELS_URL).mock(
        return_value=Response(200, json=mock_response)
    )

    response = await client.get("/models")
    assert response.status_code == 200
    models = response.json()
    assert len(models) == 2

    gemma = next(
        m for m in models if m["model_name"] == "openrouter/google/gemma-3-12b-it:free"
    )
    assert gemma["supports_input_vision"] is True
    assert gemma["supports_output_vision"] is False
    assert gemma["description"] == "A very capable model."

    gpt4 = next(m for m in models if m["model_name"] == "openrouter/openai/gpt-4o")
    assert gpt4["supports_input_vision"] is False
    assert gpt4["supports_output_vision"] is False
    assert gpt4["description"] == "The best model."
