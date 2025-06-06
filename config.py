from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_url: str = Field("sqlite:///./inventory.db", env="DATABASE_URL")
    secret_key: str = Field(..., env="SECRET_KEY")
    admin_username: str | None = Field(None, env="ADMIN_USERNAME")
    admin_password: str | None = Field(None, env="ADMIN_PASSWORD")
    next_public_api_url: str | None = Field(None, env="NEXT_PUBLIC_API_URL")
    celery_broker_url: str = Field("redis://localhost:6379/0", env="CELERY_BROKER_URL")
    stock_check_interval: int = Field(3600, env="STOCK_CHECK_INTERVAL")
    async_database_url: str | None = Field(None, env="ASYNC_DATABASE_URL")
    slack_webhook_url: str | None = Field(None, env="SLACK_WEBHOOK_URL")
    smtp_server: str | None = Field(None, env="SMTP_SERVER")
    alert_email_to: str | None = Field(None, env="ALERT_EMAIL_TO")
    alert_email_from: str = Field("noreply@example.com", env="ALERT_EMAIL_FROM")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
