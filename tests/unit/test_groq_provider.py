from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from agentos.models.contracts import ModelMessage, ModelRequest
from agentos.models.errors import ModelTimeoutError
from agentos.models.groq import GroqModelProvider


@pytest.fixture
def provider(
    monkeypatch: pytest.MonkeyPatch,
) -> GroqModelProvider:
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock()

    mock_factory = MagicMock(return_value=mock_client)

    monkeypatch.setattr(
        "agentos.models.groq.AsyncGroq",
        mock_factory,
    )

    monkeypatch.setattr(
        "agentos.models.groq.settings.model_api_key",
        MagicMock(get_secret_value=lambda: "test-key"),
    )

    return GroqModelProvider()


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
    provider: GroqModelProvider,
    request_data: ModelRequest,
) -> None:
    messages = provider._convert_messages(request_data)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == (
        "You are a helpful assistant."
    )
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Hello."


@pytest.mark.asyncio
async def test_generate_normalizes_response(
    provider: GroqModelProvider,
    request_data: ModelRequest,
) -> None:
    mock_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="Hello from Groq.",
                ),
                finish_reason="stop",
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=10,
            completion_tokens=5,
        ),
    )

    provider._client.chat.completions.create.return_value = (
        mock_response
    )

    response = await provider.generate(request_data)

    assert response.content == "Hello from Groq."
    assert response.model_name == "test-model"
    assert response.finish_reason == "stop"
    assert response.prompt_tokens == 10
    assert response.completion_tokens == 5


@pytest.mark.asyncio
async def test_generate_maps_timeout(
    provider: GroqModelProvider,
    request_data: ModelRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeTimeoutError(Exception):
        pass

    monkeypatch.setattr(
        "agentos.models.groq.APITimeoutError",
        FakeTimeoutError,
    )

    provider._client.chat.completions.create.side_effect = (
        FakeTimeoutError("Timed out")
    )

    with pytest.raises(ModelTimeoutError):
        await provider.generate(request_data)