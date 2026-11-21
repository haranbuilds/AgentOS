from typing import Any, cast

from google import genai
from google.genai import errors, types

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


class GeminiModelProvider:
    def __init__(self) -> None:
        api_key = settings.model_api_key

        if api_key is None:
            raise ValueError("MODEL_API_KEY must be configured.")

        self._client = genai.Client(
            api_key=api_key.get_secret_value(),
            http_options=types.HttpOptions(
                timeout=int(settings.model_timeout_seconds * 1000),
            ),
        ).aio

    def _convert_messages(
        self,
        request: ModelRequest,
    ) -> tuple[str | None, list[types.Content]]:
        system_instruction: str | None = None
        contents: list[types.Content] = []

        for message in request.messages:
            if message.role == "system":
                system_instruction = message.content
                continue

            if message.role == "tool":
                tool_name = self._find_tool_name(
                    request.messages,
                    message.tool_call_id,
                )

                if tool_name is None:
                    raise ModelResponseError(
                        "Unable to match tool result to a previous function call."
                    )

                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                function_response=(
                                    types.FunctionResponse(
                                        name=tool_name,
                                        id=message.tool_call_id,
                                        response={
                                            "result": message.content,
                                        },
                                    )
                                )
                            )
                        ],
                    )
                )
                continue

            parts: list[types.Part] = []

            if message.content:
                parts.append(types.Part(text=message.content))

            if message.tool_calls:
                for call in message.tool_calls:
                    parts.append(
                        types.Part(
                            function_call=types.FunctionCall(
                                name=call.name,
                                args=call.arguments,
                                id=call.id,
                            )
                        )
                    )

            contents.append(
                types.Content(
                    role=("model" if message.role == "assistant" else "user"),
                    parts=parts,
                )
            )

        return system_instruction, contents

    def _find_tool_name(
        self,
        messages: list[Any],
        tool_call_id: str | None,
    ) -> str | None:
        if tool_call_id is None:
            return None

        for message in reversed(messages):
            if not message.tool_calls:
                continue

            for call in message.tool_calls:
                if call.id == tool_call_id:
                    name = call.name
                    return name if isinstance(name, str) else None

        return None

    def _convert_tools(
        self,
        request: ModelRequest,
    ) -> list[types.Tool] | None:
        if not request.tools:
            return None

        declarations = [
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=types.Schema.model_validate(tool.parameters),
            )
            for tool in request.tools
        ]

        return [
            types.Tool(
                function_declarations=declarations,
            )
        ]

    async def generate(
        self,
        request: ModelRequest,
    ) -> ModelResponse:
        system_instruction, contents = self._convert_messages(request)

        tools = self._convert_tools(request)

        config = types.GenerateContentConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
            system_instruction=system_instruction,
            tools=cast(Any, tools),
        )

        try:
            response = await self._client.models.generate_content(
                model=request.model_name,
                contents=contents,
                config=config,
            )

            usage = response.usage_metadata
            finish_reason = None
            normalized_tool_calls: list[ToolCall] = []

            if response.candidates:
                candidate = response.candidates[0]

                if candidate.finish_reason is not None:
                    finish_reason = candidate.finish_reason.name.lower()

                if candidate.content and candidate.content.parts:
                    for index, part in enumerate(candidate.content.parts):
                        function_call = part.function_call

                        if function_call is None:
                            continue

                        normalized_tool_calls.append(
                            ToolCall(
                                id=(function_call.id or f"gemini_call_{index}"),
                                name=function_call.name or "",
                                arguments=(dict(function_call.args) if function_call.args else {}),
                            )
                        )

            return ModelResponse(
                content=response.text or "",
                model_name=request.model_name,
                finish_reason=finish_reason,
                prompt_tokens=(usage.prompt_token_count if usage is not None else None),
                completion_tokens=(usage.candidates_token_count if usage is not None else None),
                tool_calls=normalized_tool_calls,
            )

        except TimeoutError as exc:
            raise ModelTimeoutError("Gemini request timed out.") from exc

        except errors.APIError as exc:
            if exc.code in (401, 403):
                raise ModelAuthenticationError("Gemini authentication failed.") from exc

            if exc.code == 429:
                raise ModelRateLimitError("Gemini rate limit exceeded.") from exc

            if exc.code is not None and exc.code >= 500:
                raise ModelUnavailableError("Gemini service is unavailable.") from exc

            raise ModelProviderError("Gemini request failed.") from exc
