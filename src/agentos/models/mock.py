from agentos.models.contracts import ModelRequest, ModelResponse


class MockModelProvider:
    async def generate(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            content="Mock model response",
            model_name=request.model_name,
            finish_reason="stop",
            prompt_tokens=10,
            completion_tokens=5,
        )
