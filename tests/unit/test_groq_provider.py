from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from agentos.models.contracts import (
    ModelMessage,
    ModelRequest,
)
from agentos.models.errors import ModelTimeoutError
from agentos.models.groq import GroqModelProvider


@pytest.fixture
def provider(
    monkeypatch: pytest.MonkeyPatch,
) -> GroqModelProvider:
    monkeypatch.setattr(
        "agentos.models.groq.settings.model_api_key",
        MagicMock(get_secret_value=lambda: "test-api-key"),
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock()

    monkeypatch.setattr(
        "agentos.models.groq.AsyncGroq",
        MagicMock(return_value=mock_client),
    )

    instance = GroqModelProvider()
    instance._client = mock_client

    return instance


@pytest.fixture
def request_data() -> ModelRequest:
    return ModelRequest(
        messages=[
            ModelMessage(
                role="user",
                content="Hello",
            )
        ],
        model_name="test-model",
    )


def test_convert_messages(
    provider: GroqModelProvider,
    request_data: ModelRequest,
) -> None:
    messages = provider._convert_messages(request_data)

    assert messages == [
        {
            "role": "user",
            "content": "Hello",
        }
    ]


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
                    tool_calls=None,
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
    assert response.tool_calls == []


@pytest.mark.asyncio
async def test_generate_timeout(
    provider: GroqModelProvider,
    request_data: ModelRequest,
) -> None:
    from groq import APITimeoutError

    provider._client.chat.completions.create.side_effect = (
        APITimeoutError(
            request=MagicMock(),
        )
    )

    with pytest.raises(ModelTimeoutError):
        await provider.generate(request_data)


@pytest.mark.asyncio
async def test_generate_normalizes_tool_call(
    provider: GroqModelProvider,
    request_data: ModelRequest,
) -> None:
    mock_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[
                        SimpleNamespace(
                            id="call_001",
                            function=SimpleNamespace(
                                name="get_balance",
                                arguments='{"account_id": "A100"}',
                            ),
                        )
                    ],
                ),
                finish_reason="tool_calls",
            )
        ],
        usage=None,
    )

    provider._client.chat.completions.create.return_value = (
        mock_response
    )

    response = await provider.generate(request_data)

    assert response.content == ""
    assert response.finish_reason == "tool_calls"
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].id == "call_001"
    assert response.tool_calls[0].name == "get_balance"
    assert response.tool_calls[0].arguments == {
        "account_id": "A100",
    }