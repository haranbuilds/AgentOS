from agentos.models.contracts import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ToolCall,
    ToolDefinition,
)


def test_tool_definition_contract() -> None:
    tool = ToolDefinition(
        name="get_balance",
        description="Get an account balance.",
        parameters={
            "type": "object",
            "properties": {
                "account_id": {"type": "string"},
            },
            "required": ["account_id"],
        },
    )

    assert tool.name == "get_balance"
    assert tool.parameters["type"] == "object"


def test_tool_call_contract() -> None:
    tool_call = ToolCall(
        id="call_001",
        name="get_balance",
        arguments={"account_id": "A100"},
    )

    assert tool_call.id == "call_001"
    assert tool_call.name == "get_balance"
    assert tool_call.arguments["account_id"] == "A100"


def test_assistant_tool_call_message() -> None:
    message = ModelMessage(
        role="assistant",
        content="",
        tool_calls=[
            ToolCall(
                id="call_001",
                name="get_balance",
                arguments={"account_id": "A100"},
            )
        ],
    )

    assert message.role == "assistant"
    assert message.tool_calls is not None
    assert message.tool_calls[0].name == "get_balance"


def test_tool_result_message() -> None:
    message = ModelMessage(
        role="tool",
        content='{"balance": 5000}',
        tool_call_id="call_001",
    )

    assert message.role == "tool"
    assert message.tool_call_id == "call_001"


def test_model_request_with_tools() -> None:
    request = ModelRequest(
        messages=[
            ModelMessage(
                role="user",
                content="Check my balance.",
            )
        ],
        model_name="test-model",
        tools=[
            ToolDefinition(
                name="get_balance",
                description="Get an account balance.",
                parameters={"type": "object"},
            )
        ],
    )

    assert request.tools is not None
    assert request.tools[0].name == "get_balance"


def test_model_response_with_tool_calls() -> None:
    response = ModelResponse(
        content="",
        model_name="test-model",
        tool_calls=[
            ToolCall(
                id="call_001",
                name="get_balance",
                arguments={"account_id": "A100"},
            )
        ],
    )

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].id == "call_001"


def test_model_response_without_tool_calls() -> None:
    response = ModelResponse(
        content="Hello.",
        model_name="test-model",
    )

    assert response.tool_calls == []
