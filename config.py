from functools import lru_cache

try:
    from pydantic_settings import BaseSettings  # type: ignore
    from pydantic import Field, ConfigDict
except Exception:  # fallback if package missing or using pydantic v1
    try:
        from pydantic_settings_stub import BaseSettings  # type: ignore
    except Exception:
        from pydantic import BaseSettings  # type: ignore
    from pydantic import Field

    ConfigDict = None

from secrets_manager import get_manager


class Settings(BaseSettings):
    if ConfigDict is not None:
        model_config = ConfigDict(extra="ignore", env_file=".env")
    else:

        class Config:
            extra = "ignore"
            env_file = ".env"

    database_url: str = Field("sqlite:///./inventory.db", env="DATABASE_URL")
    secret_key: str | None = Field(None, env="SECRET_KEY")
    secret_store_file: str | None = Field(None, env="SECRET_STORE_FILE")
    admin_username: str | None = Field(None, env="ADMIN_USERNAME")
    admin_password: str | None = Field(None, env="ADMIN_PASSWORD")
    next_public_api_url: str | None = Field(None, env="NEXT_PUBLIC_API_URL")
    cors_allow_origins: str | None = Field(None, env="CORS_ALLOW_ORIGINS")
    celery_broker_url: str = Field("redis://localhost:6379/0", env="CELERY_BROKER_URL")
    redis_url: str = Field("redis://localhost:6379/1", env="REDIS_URL")
    rate_limit_redis_url: str = Field("memory://", env="RATE_LIMIT_REDIS_URL")
    stock_check_interval: int = Field(3600, env="STOCK_CHECK_INTERVAL")
    async_database_url: str | None = Field(None, env="ASYNC_DATABASE_URL")
    slack_webhook_url: str | None = Field(None, env="SLACK_WEBHOOK_URL")
    smtp_server: str | None = Field(None, env="SMTP_SERVER")
    alert_email_to: str | None = Field(None, env="ALERT_EMAIL_TO")
    alert_email_from: str = Field("noreply@example.com", env="ALERT_EMAIL_FROM")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    if not settings.secret_key and settings.secret_store_file:
        manager = get_manager(settings.secret_store_file)
        if manager:
            secret = manager.get_secret("SECRET_KEY")
            if secret:
                settings.secret_key = secret
    if settings.secret_key is None:
        settings.secret_key = "changeme"
    return settings


settings = get_settings()
