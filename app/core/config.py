from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["dev", "test", "stage", "prod"] = "dev"
    app_name: str = "enterprise-ai-resume-generator"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"

    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    app_user_username: str = "resume_user"
    app_user_password_hash: str

    openai_api_key: str
    openai_model: str
    llm_timeout_seconds: int = Field(default=60, ge=5, le=300)
    llm_max_retries: int = Field(default=2, ge=0, le=5)

    max_review_revisions: int = Field(default=1, ge=0, le=3)
    review_pass_score: int = Field(default=85, ge=50, le=100)

    metrics_enabled: bool = True
    otel_enabled: bool = False
    otel_service_name: str = "enterprise-ai-resume-generator"
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]

    @field_validator("jwt_secret")
    @classmethod
    def reject_weak_default_secret(cls, value: str) -> str:
        weak = {"replace-with-at-least-32-random-characters", "changeme", "secret"}
        if value.lower() in weak:
            raise ValueError("JWT_SECRET must be replaced with a strong random secret.")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
