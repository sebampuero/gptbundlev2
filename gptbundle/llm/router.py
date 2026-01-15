import logging

import httpx
from fastapi import APIRouter

from gptbundle.common.config import settings

from .models import LLMModel

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/models", response_model=list[LLMModel])
async def get_models():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.OPENROUTER_MODELS_URL,
            headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
        )
        response.raise_for_status()
        data = response.json()

    models = []
    for model_data in data["data"]:
        if "id" not in model_data:
            continue

        architecture = model_data.get("architecture", {})
        modalities = architecture.get("modality", "")

        supports_input_vision = "image" in architecture.get("input_modalities", [])
        supports_output_vision = "image" in architecture.get("output_modalities", [])

        if not supports_input_vision and "image" in modalities and "->" in modalities:
            input_part = modalities.split("->")[0]
            if "image" in input_part:
                supports_input_vision = True

        models.append(
            LLMModel(
                model_name=f"openrouter/{model_data['id']}",  # TODO: hardcoded for now
                description=model_data.get("description", ""),
                supports_input_vision=supports_input_vision,
                supports_output_vision=supports_output_vision,
            )
        )
    return models
