"""
Core configuration module using pydantic-settings for type-safe configuration.
Supports .env files and environment variables.
"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    url: str = Field(
        default="postgresql+asyncpg://awfdrs:awfdrs@localhost:5432/awfdrs",
        alias="DATABASE_URL"
    )
    pool_size: int = Field(default=20, alias="DATABASE_POOL_SIZE")
    pool_timeout: int = Field(default=30, alias="DATABASE_POOL_TIMEOUT")
    echo: bool = Field(default=False, alias="DATABASE_ECHO")


class RedisSettings(BaseSettings):
    """Redis configuration."""

    url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    max_connections: int = Field(default=50, alias="REDIS_MAX_CONNECTIONS")


class AISettings(BaseSettings):
    """AI configuration - ALWAYS MOCK for this project."""

    mode: str = Field(default="mock", alias="AI_MODE")
    openai_api_key: str = Field(default="mock-key-no-real-calls", alias="OPENAI_API_KEY")
    pinecone_api_key: str = Field(default="mock-key-no-real-calls", alias="PINECONE_API_KEY")
    confidence_threshold: float = Field(default=0.7, alias="AI_CONFIDENCE_THRESHOLD")

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Ensure AI mode is always mock for this project."""
        if v != "mock":
            raise ValueError("AI mode must be 'mock' - real API calls are disabled for this project")
        return v


class AuthSettings(BaseSettings):
    """Authentication configuration."""

    jwt_secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        alias="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")


class SafetyLimits(BaseSettings):
    """Safety limits and circuit breaker configuration."""

    max_retries_per_workflow: int = Field(default=5, alias="MAX_RETRIES_PER_WORKFLOW")
    max_retries_per_vendor: int = Field(default=100, alias="MAX_RETRIES_PER_VENDOR")
    circuit_breaker_threshold: int = Field(default=10, alias="CIRCUIT_BREAKER_THRESHOLD")
    circuit_breaker_timeout_seconds: int = Field(
        default=300,
        alias="CIRCUIT_BREAKER_TIMEOUT_SECONDS"
    )


class FeatureFlags(BaseSettings):
    """Feature flags for enabling/disabling functionality."""

    enable_ai_detection: bool = Field(default=False, alias="ENABLE_AI_DETECTION")
    enable_ai_rca: bool = Field(default=False, alias="ENABLE_AI_RCA")
    enable_auto_retry: bool = Field(default=False, alias="ENABLE_AUTO_RETRY")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application settings
    app_name: str = "AWFDRS"
    app_version: str = "0.1.0"
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    enable_tracing: bool = Field(default=True, alias="ENABLE_TRACING")

    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        alias="CORS_ORIGINS"
    )

    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    ai: AISettings = Field(default_factory=AISettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    safety: SafetyLimits = Field(default_factory=SafetyLimits)
    features: FeatureFlags = Field(default_factory=FeatureFlags)

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string if needed."""
        if isinstance(v, str):
            return json.loads(v)
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper


# Global settings instance
settings = Settings()
