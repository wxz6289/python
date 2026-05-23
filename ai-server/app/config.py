from functools import lru_cache
from typing import Self
from urllib.parse import quote_plus

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.infra.compose import get_mysql_compose_config, get_redis_compose_config


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    redis_url: str | None = None
    redis_ttl_seconds: int = 60 * 60 * 24 * 7
    host: str = "127.0.0.1"
    port: int = 8000

    mysql_host: str | None = None
    mysql_port: int | None = None
    mysql_user: str | None = None
    mysql_password: str | None = None
    mysql_database: str | None = None

    jwt_secret: str = "ai-server-jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    @model_validator(mode="after")
    def apply_compose_defaults(self) -> Self:
        mysql = get_mysql_compose_config()
        if self.mysql_host is None:
            self.mysql_host = str(mysql["host"])
        if self.mysql_port is None:
            self.mysql_port = int(mysql["port"])
        if self.mysql_user is None:
            self.mysql_user = str(mysql["user"])
        if self.mysql_password is None:
            self.mysql_password = str(mysql["password"])
        if self.mysql_database is None:
            self.mysql_database = str(mysql["database"])
        if self.redis_url is None:
            self.redis_url = str(get_redis_compose_config()["url"])
        return self

    @model_validator(mode="after")
    def require_deepseek_api_key(self) -> Self:
        if not self.deepseek_api_key.strip():
            msg = "DEEPSEEK_API_KEY is required (set in .env)"
            raise ValueError(msg)
        return self

    @property
    def database_url(self) -> str:
        password = quote_plus(self.mysql_password or "")
        return (
            f"mysql+aiomysql://{self.mysql_user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def tortoise_database_url(self) -> str:
        """Tortoise ORM 使用的 MySQL 连接串（asyncmy 驱动）。"""
        password = quote_plus(self.mysql_password or "")
        return (
            f"mysql://{self.mysql_user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
