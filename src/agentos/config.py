from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AgentOS"
    app_env: Literal["development", "test", "production"] = "development"
    app_debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    api_host: str = "127.0.0.1"
    api_port: int = 8000

    database_url: str = "postgresql://agentos:agentos_dev@localhost:5432/agentos"
    redis_url: str = "redis://localhost:6379/0"

    model_provider: str | None = None
    model_name: str | None = None
    model_api_key: SecretStr | None = None

    otel_enabled: bool = False
    model_timeout_seconds: float = Field(default=30.0, gt=0)
    model_max_retries: int = Field(default=2, ge=0, le=5)


settings = Settings()
