from pydantic import Field, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App Settings
    APP_NAME: str = "Fastbin"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost/fastbin",
        description="PostgreSQL connection string",
    )
    TEST_DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost/fastbin",
        description="PostgreSQL connection string for testing",
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379", description="Redis connection string"
    )

    # JWT
    SECRET_KEY: str = Field(
        default=secrets.token_urlsafe(32),
        min_length=32,
        description="Secret key for JWT (must be 32+ chars)",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: str = "10/minute"
    AUTHENTICATED_RATE_LIMIT: str = "100/minute"

    # Notifications
    ENABLE_NOTIFICATIONS: bool = False
    NOTIFICATION_EMAIL_FROM: EmailStr = "noreply@fastbin.com"

    # SMTP (Optional)
    SMTP_HOST: str = "smtp.gmail.com"
    SMPT_PORT: int = 587
    SMPT_USER: str = ""
    SMTP_PASSWORD: str = Field(default="", repr=False)  # Hidden in logs

    # Analytics
    ANALYTICS_BATCH_SIZE: int = 100
    ANALYTICS_RETENTION_DAYS: int = 90


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
