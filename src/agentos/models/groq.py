import json
from typing import Any

from groq import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AsyncGroq,
)

from agentos.config import settings
from agentos.models.contracts import (
    ModelRequest,
    ModelResponse,
    ToolCall,
)
from agentos.models.errors import (
    ModelAuthenticationError,
    ModelProviderError,
    ModelRateLimitError,
    ModelResponseError,
    ModelTimeoutError,
    ModelUnavailableError,
)


class GroqModelProvider:
    def __init__(self) -> None:
        api_key = settings.model_api_key

        if api_key is None:
            raise ValueError(
                "MODEL_API_KEY must be configured."
            )

        self._client = AsyncGroq(
            api_key=api_key.get_secret_value(),
            timeout=settings.model_timeout_seconds,
        )

    def _convert_messages(
        self,
        request: ModelRequest,
    ) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []

        for message in request.messages:
            converted: dict[str, Any] = {
                "role": message.role,
                "content": message.content,
            }

            if message.tool_call_id is not None:
                converted["tool_call_id"] = message.tool_call_id

            if message.tool_calls:
                converted["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.name,
                            "arguments": json.dumps(
                                call.arguments
                            ),
                        },
                    }
                    for call in message.tool_calls
                ]

            messages.append(converted)

        return messages

    def _convert_tools(
        self,
        request: ModelRequest,
    ) -> list[dict[str, Any]] | None:
        if not request.tools:
            return None

        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in request.tools
        ]

    async def generate(
        self,
        request: ModelRequest,
    ) -> ModelResponse:
        messages = self._convert_messages(request)
        tools = self._convert_tools(request)

        try:
            response = await self._client.chat.completions.create(
                model=request.model_name,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=tools,
            )

            choice = response.choices[0]
            usage = response.usage
            normalized_tool_calls: list[ToolCall] = []

            if choice.message.tool_calls:
                for call in choice.message.tool_calls:
                    try:
                        arguments = json.loads(
                            call.function.arguments
                        )
                    except json.JSONDecodeError as exc:
                        raise ModelResponseError(
                            "Groq returned invalid tool arguments."
                        ) from exc

                    if not isinstance(arguments, dict):
                        raise ModelResponseError(
                            "Tool arguments must be a JSON object."
                        )

                    normalized_tool_calls.append(
                        ToolCall(
                            id=call.id,
                            name=call.function.name,
                            arguments=arguments,
                        )
                    )

            return ModelResponse(
                content=choice.message.content or "",
                model_name=request.model_name,
                finish_reason=choice.finish_reason,
                prompt_tokens=(
                    usage.prompt_tokens
                    if usage is not None
                    else None
                ),
                completion_tokens=(
                    usage.completion_tokens
                    if usage is not None
                    else None
                ),
                tool_calls=normalized_tool_calls,
            )

        except APITimeoutError as exc:
            raise ModelTimeoutError(
                "Groq request timed out."
            ) from exc

        except APIConnectionError as exc:
            raise ModelUnavailableError(
                "Unable to connect to Groq."
            ) from exc

        except APIError as exc:
            if exc.status_code in (401, 403):
                raise ModelAuthenticationError(
                    "Groq authentication failed."
                ) from exc

            if exc.status_code == 429:
                raise ModelRateLimitError(
                    "Groq rate limit exceeded."
                ) from exc

            if (
                exc.status_code is not None
                and exc.status_code >= 500
            ):
                raise ModelUnavailableError(
                    "Groq service is unavailable."
                ) from exc

            raise ModelProviderError(
                "Groq request failed."
            ) from exc