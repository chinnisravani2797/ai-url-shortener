from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./url_shortener.db"
    app_env: str = "development"
    debug: bool = False
    analytics_api_key: str | None = None
    rate_limit_per_minute: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
