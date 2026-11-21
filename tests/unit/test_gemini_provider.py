from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from agentos.models.contracts import ModelMessage, ModelRequest
from agentos.models.errors import (
    ModelAuthenticationError,
    ModelTimeoutError,
)
from agentos.models.gemini import GeminiModelProvider


@pytest.fixture
def provider(monkeypatch: pytest.MonkeyPatch) -> GeminiModelProvider:
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock()

    mock_factory = MagicMock(return_value=mock_client)
    monkeypatch.setattr(
        "agentos.models.gemini.genai.Client",
        mock_factory,
    )

    monkeypatch.setattr(
        "agentos.models.gemini.settings.model_api_key",
        MagicMock(get_secret_value=lambda: "test-key"),
    )

    return GeminiModelProvider()


@pytest.fixture
def request_data() -> ModelRequest:
    return ModelRequest(
        messages=[
            ModelMessage(
                role="system",
                content="You are a helpful assistant.",
            ),
            ModelMessage(
                role="user",
                content="Hello.",
            ),
        ],
        model_name="test-model",
    )


def test_message_conversion(
    provider: GeminiModelProvider,
    request_data: ModelRequest,
) -> None:
    system_instruction, contents = provider._convert_messages(
        request_data
    )

    assert system_instruction == "You are a helpful assistant."
    assert len(contents) == 1
    assert contents[0].role == "user"
    assert contents[0].parts[0].text == "Hello."


@pytest.mark.asyncio
async def test_generate_normalizes_response(
    provider: GeminiModelProvider,
    request_data: ModelRequest,
) -> None:
    mock_response = MagicMock()

    mock_response.text = "Hello from Gemini."

    mock_response.candidates = [
        SimpleNamespace(
            finish_reason=SimpleNamespace(name="STOP")
        )
    ]

    mock_response.usage_metadata = SimpleNamespace(
        prompt_token_count=10,
        candidates_token_count=5,
    )

    provider._client.models.generate_content.return_value = (
        mock_response
    )

    response = await provider.generate(request_data)

    assert response.content == "Hello from Gemini."
    assert response.model_name == "test-model"
    assert response.finish_reason == "stop"
    assert response.prompt_tokens == 10
    assert response.completion_tokens == 5


@pytest.mark.asyncio
async def test_generate_maps_timeout(
    provider: GeminiModelProvider,
    request_data: ModelRequest,
) -> None:
    provider._client.models.generate_content.side_effect = (
        TimeoutError
    )

    with pytest.raises(ModelTimeoutError):
        await provider.generate(request_data)


@pytest.mark.asyncio
async def test_generate_maps_authentication_error(
    provider: GeminiModelProvider,
    request_data: ModelRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeAPIError(Exception):
        code = 401

    monkeypatch.setattr(
        "agentos.models.gemini.errors.APIError",
        FakeAPIError,
    )

    provider._client.models.generate_content.side_effect = (
        FakeAPIError("Unauthorized")
    )

    with pytest.raises(ModelAuthenticationError):
        await provider.generate(request_data)