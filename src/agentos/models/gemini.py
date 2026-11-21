from google import genai
from google.genai import errors, types

from agentos.config import settings
from agentos.models.contracts import ModelRequest, ModelResponse
from agentos.models.errors import (
    ModelAuthenticationError,
    ModelProviderError,
    ModelRateLimitError,
    ModelTimeoutError,
    ModelUnavailableError,
)


class GeminiModelProvider:
    def __init__(self) -> None:
        api_key = settings.model_api_key

        if api_key is None:
            raise ValueError(
                "MODEL_API_KEY must be configured."
            )

        self._client = genai.Client(
            api_key=api_key.get_secret_value(),
            http_options=types.HttpOptions(
                timeout=int(
                    settings.model_timeout_seconds * 1000
                ),
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

            role = (
                "model"
                if message.role == "assistant"
                else "user"
            )

            contents.append(
                types.Content(
                    role=role,
                    parts=[
                        types.Part(text=message.content),
                    ],
                )
            )

        return system_instruction, contents

    async def generate(
        self,
        request: ModelRequest,
    ) -> ModelResponse:
        system_instruction, contents = self._convert_messages(
            request
        )

        config = types.GenerateContentConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
            system_instruction=system_instruction,
        )

        try:
            response = await self._client.models.generate_content(
                model=request.model_name,
                contents=contents,
                config=config,
            )

            usage = response.usage_metadata

            finish_reason = None

            if response.candidates:
                candidate = response.candidates[0]

                if candidate.finish_reason is not None:
                    finish_reason = (
                        candidate.finish_reason.name.lower()
                    )

            return ModelResponse(
                content=response.text or "",
                model_name=request.model_name,
                finish_reason=finish_reason,
                prompt_tokens=(
                    usage.prompt_token_count
                    if usage is not None
                    else None
                ),
                completion_tokens=(
                    usage.candidates_token_count
                    if usage is not None
                    else None
                ),
            )

        except TimeoutError as exc:
            raise ModelTimeoutError(
                "Gemini request timed out."
            ) from exc

        except errors.APIError as exc:
            if exc.code in (401, 403):
                raise ModelAuthenticationError(
                    "Gemini authentication failed."
                ) from exc

            if exc.code == 429:
                raise ModelRateLimitError(
                    "Gemini rate limit exceeded."
                ) from exc

            if exc.code is not None and exc.code >= 500:
                raise ModelUnavailableError(
                    "Gemini service is unavailable."
                ) from exc

            raise ModelProviderError(
                "Gemini request failed."
            ) from exc