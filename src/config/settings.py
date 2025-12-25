"""
Production configuration settings for Sankore Intelligence Layer.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings can be configured via environment variables.
    """

    # Application
    APP_NAME: str = "Sankore Intelligence API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # CORS
    ALLOWED_ORIGINS: str = "*"

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v) -> List[str]:
        """Parse comma-separated origins into list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",")]
        return v

    # API Keys
    OPENAI_API_KEY: str = ""
    META_API_KEY: str = ""
    TIKTOK_ACCESS_TOKEN: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    # Database Connection Pooling
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True

    # API Rate Limiting (future use)
    RATE_LIMIT_PER_MINUTE: int = 60

    # Cache Settings (Redis - future use)
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 300  # 5 minutes

    # OpenAI Settings
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7

    # Trend Settings
    DEFAULT_TREND_LIMIT: int = 10
    MAX_TREND_LIMIT: int = 100
    TREND_CACHE_TTL: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Settings: Application configuration
    """
    return settings


# Validation on import
def validate_production_settings():
    """
    Validate critical settings for production environment.

    Raises:
        ValueError: If required production settings are missing or invalid
    """
    if settings.ENVIRONMENT == "production":
        errors = []

        # Check secret key
        if settings.SECRET_KEY == "change-me-in-production":
            errors.append("SECRET_KEY must be changed in production")

        # Check debug mode
        if settings.DEBUG:
            errors.append("DEBUG must be False in production")

        # Check database
        if settings.DATABASE_URL.startswith("sqlite"):
            errors.append("SQLite is not recommended for production - use PostgreSQL")

        # Check CORS
        if settings.ALLOWED_ORIGINS == ["*"]:
            errors.append("ALLOWED_ORIGINS should be restricted in production")

        # Check OpenAI key
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-mock"):
            errors.append("Valid OPENAI_API_KEY required in production")

        if errors:
            raise ValueError(
                "Production configuration errors:\n" + "\n".join(f"- {e}" for e in errors)
            )


# Run validation on import (can be disabled for testing)
if os.getenv("SKIP_SETTINGS_VALIDATION") != "true":
    try:
        validate_production_settings()
    except ValueError as e:
        if settings.ENVIRONMENT == "production":
            raise
        # In development, just warn
        import logging
        logging.warning(f"Settings validation warnings: {e}")
