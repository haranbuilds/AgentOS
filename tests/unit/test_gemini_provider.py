from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from agentos.models.contracts import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ToolCall,
    ToolDefinition,
)
from agentos.models.errors import (
    ModelAuthenticationError,
    ModelResponseError,
    ModelTimeoutError,
)
from agentos.models.gemini import GeminiModelProvider


@pytest.fixture
def provider(
    monkeypatch: pytest.MonkeyPatch,
) -> GeminiModelProvider:
    monkeypatch.setattr(
        "agentos.models.gemini.settings.model_api_key",
        MagicMock(get_secret_value=lambda: "test-api-key"),
    )

    mock_client = MagicMock()
    mock_client.models.generate_content = AsyncMock()

    monkeypatch.setattr(
        "agentos.models.gemini.genai.Client",
        MagicMock(return_value=SimpleNamespace(aio=mock_client)),
    )

    instance = GeminiModelProvider()
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
    provider: GeminiModelProvider,
    request_data: ModelRequest,
) -> None:
    system_instruction, contents = provider._convert_messages(request_data)

    assert system_instruction is None
    assert len(contents) == 1
    assert contents[0].role == "user"
    assert contents[0].parts is not None
    assert contents[0].parts[0].text == "Hello"


@pytest.mark.asyncio
async def test_generate_normalizes_response(
    provider: GeminiModelProvider,
    request_data: ModelRequest,
) -> None:
    generate_content = cast(
        AsyncMock,
        provider._client.models.generate_content,
    )
    generate_content.return_value = SimpleNamespace(
        text="Hello from Gemini.",
        candidates=[
            SimpleNamespace(
                finish_reason=SimpleNamespace(
                    name="STOP",
                ),
                content=SimpleNamespace(
                    parts=[
                        SimpleNamespace(
                            function_call=None,
                        )
                    ]
                ),
            )
        ],
        usage_metadata=SimpleNamespace(
            prompt_token_count=10,
            candidates_token_count=5,
        ),
    )

    response = await provider.generate(request_data)

    assert isinstance(response, ModelResponse)
    assert response.content == "Hello from Gemini."
    assert response.model_name == "test-model"
    assert response.finish_reason == "stop"
    assert response.prompt_tokens == 10
    assert response.completion_tokens == 5
    assert response.tool_calls == []


@pytest.mark.asyncio
async def test_generate_timeout(
    provider: GeminiModelProvider,
    request_data: ModelRequest,
) -> None:
    generate_content = cast(
        AsyncMock,
        provider._client.models.generate_content,
    )
    generate_content.side_effect = TimeoutError

    with pytest.raises(ModelTimeoutError):
        await provider.generate(request_data)


@pytest.mark.asyncio
async def test_generate_authentication_error(
    provider: GeminiModelProvider,
    request_data: ModelRequest,
) -> None:
    from google.genai.errors import APIError

    generate_content = cast(
        AsyncMock,
        provider._client.models.generate_content,
    )
    generate_content.side_effect = APIError(
        code=401,
        response_json={"error": {"message": "Unauthorized"}},
    )

    with pytest.raises(ModelAuthenticationError):
        await provider.generate(request_data)


def test_convert_tools(
    provider: GeminiModelProvider,
    request_data: ModelRequest,
) -> None:
    request = request_data.model_copy(
        update={
            "tools": [
                ToolDefinition(
                    name="get_balance",
                    description="Get account balance.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "account_id": {
                                "type": "string",
                            },
                        },
                    },
                )
            ]
        }
    )

    tools = provider._convert_tools(request)

    assert tools is not None
    assert len(tools) == 1
    declarations = tools[0].function_declarations
    assert declarations is not None
    assert declarations[0].name == ("get_balance")


def test_convert_assistant_tool_call_history(
    provider: GeminiModelProvider,
) -> None:
    request = ModelRequest(
        model_name="test-model",
        messages=[
            ModelMessage(
                role="assistant",
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="get_balance",
                        arguments={
                            "account_id": "A100",
                        },
                    )
                ],
            )
        ],
    )

    _, contents = provider._convert_messages(request)

    parts = contents[0].parts
    assert parts is not None
    function_call = parts[0].function_call

    assert function_call is not None
    assert function_call.name == "get_balance"
    assert function_call.args == {
        "account_id": "A100",
    }


def test_convert_tool_result_history(
    provider: GeminiModelProvider,
) -> None:
    request = ModelRequest(
        model_name="test-model",
        messages=[
            ModelMessage(
                role="assistant",
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="get_balance",
                        arguments={
                            "account_id": "A100",
                        },
                    )
                ],
            ),
            ModelMessage(
                role="tool",
                content='{"balance": 5000}',
                tool_call_id="call_001",
            ),
        ],
    )

    _, contents = provider._convert_messages(request)

    parts = contents[1].parts
    assert parts is not None
    function_response = parts[0].function_response

    assert function_response is not None
    assert function_response.name == "get_balance"
    assert function_response.id == "call_001"


def test_unmatched_tool_result_id(
    provider: GeminiModelProvider,
) -> None:
    request = ModelRequest(
        model_name="test-model",
        messages=[
            ModelMessage(
                role="tool",
                content="result",
                tool_call_id="unknown_call",
            )
        ],
    )

    with pytest.raises(ModelResponseError):
        provider._convert_messages(request)
