import pytest

from agentos.models.contracts import ModelMessage, ModelRequest
from agentos.models.mock import MockModelProvider
from agentos.models.protocol import ModelProvider


@pytest.mark.asyncio
async def test_mock_provider_satisfies_provider_contract() -> None:
    provider: ModelProvider = MockModelProvider()
    request = ModelRequest(
        messages=[
            ModelMessage(
                role="user",
                content="hello",
            )
        ],
        model_name="mock-model",
    )

    response = await provider.generate(request)

    assert response.content == "Mock model response"
    assert response.model_name == "mock-model"
    assert response.finish_reason == "stop"
    assert response.prompt_tokens == 10
    assert response.completion_tokens == 5
