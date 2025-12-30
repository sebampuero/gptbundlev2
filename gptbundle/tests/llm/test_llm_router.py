import pytest
import respx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

from gptbundle.common.config import settings
from gptbundle.llm.router import router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@respx.mock
def test_get_models(client):
    mock_response = {
        "data": [
            {
                "id": "google/gemma-3-12b-it:free",
                "architecture": {
                    "modality": "text+image->text",
                    "input_modalities": ["text", "image"],
                    "output_modalities": ["text"],
                },
            },
            {
                "id": "openai/gpt-4o",
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

    response = client.get("/models")
    assert response.status_code == 200
    models = response.json()
    assert len(models) == 2

    gemma = next(m for m in models if m["model_name"] == "google/gemma-3-12b-it:free")
    assert gemma["supports_input_vision"] is True
    assert gemma["supports_output_vision"] is False

    gpt4 = next(m for m in models if m["model_name"] == "openai/gpt-4o")
    assert gpt4["supports_input_vision"] is False
    assert gpt4["supports_output_vision"] is False
