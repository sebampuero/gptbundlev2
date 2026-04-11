from pydantic import BaseModel


class LLMModel(BaseModel):
    model_name: str
    description: str
    supports_input_vision: bool
    supports_output_vision: bool
    supports_reasoning: bool
