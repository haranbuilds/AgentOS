from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ToolCall(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    arguments: dict[str, Any]


class ToolDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    description: str
    parameters: dict[str, Any]


class ModelMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_call_id: str | None = None
    tool_calls: list[ToolCall] | None = None


class ModelRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    messages: list[ModelMessage]
    model_name: str
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)
    tools: list[ToolDefinition] | None = None


class ModelResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    content: str
    model_name: str
    finish_reason: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)