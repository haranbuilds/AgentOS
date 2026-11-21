from groq import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AsyncGroq,
)

from agentos.config import settings
from agentos.models.contracts import ModelRequest, ModelResponse
from agentos.models.errors import (
    ModelAuthenticationError,
    ModelProviderError,
    ModelRateLimitError,
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
    ) -> list[dict[str, str]]:
        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.messages
        ]

    async def generate(
        self,
        request: ModelRequest,
    ) -> ModelResponse:
        messages = self._convert_messages(request)

        try:
            response = await self._client.chat.completions.create(
                model=request.model_name,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            choice = response.choices[0]
            usage = response.usage

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