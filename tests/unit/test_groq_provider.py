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
    assert response.tool_calls[0].name == "get_balance"
    assert response.tool_calls[0].arguments == {
        "account_id": "A100",
    }