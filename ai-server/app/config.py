from functools import lru_cache
from typing import Literal, Self
from urllib.parse import quote_plus

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.infra.compose import get_mysql_compose_config, get_redis_compose_config

LlmProvider = Literal["auto", "deepseek", "closeai"]


def normalize_deepseek_base_url(base_url: str) -> str:
    url = base_url.strip().rstrip("/")
    if not url:
        return "https://api.deepseek.com"
    if url.endswith("/v1"):
        return url[: -len("/v1")]
    return url


def normalize_openai_compatible_base_url(base_url: str) -> str:
    url = base_url.strip().rstrip("/")
    if not url:
        return "https://api.openai-proxy.org/v1"
    if url.endswith("/v1"):
        return url
    return f"{url}/v1"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat-v4-flash"
    closeai_api_key: str = ""
    closeai_base_url: str = "https://api.openai-proxy.org/v1"
    llm_provider: LlmProvider = "auto"
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

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Prefer project .env over exported shell variables during local development.
        return (
            init_settings,
            dotenv_settings,
            env_settings,
            file_secret_settings,
        )

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
    def normalize_llm_settings(self) -> Self:
        self.deepseek_api_key = self.deepseek_api_key.strip()
        self.closeai_api_key = self.closeai_api_key.strip()
        self.deepseek_base_url = normalize_deepseek_base_url(self.deepseek_base_url)
        self.closeai_base_url = normalize_openai_compatible_base_url(
            self.closeai_base_url
        )
        self.deepseek_model = self.deepseek_model.strip() or "deepseek-chat"
        return self

    @model_validator(mode="after")
    def require_llm_api_key(self) -> Self:
        if not self.llm_api_key:
            msg = "DEEPSEEK_API_KEY or CLOSEAI_API_KEY is required (set in .env)"
            raise ValueError(msg)
        return self

    @property
    def resolved_llm_provider(self) -> Literal["deepseek", "closeai"]:
        if self.llm_provider == "deepseek":
            return "deepseek"
        if self.llm_provider == "closeai":
            return "closeai"
        if self.closeai_api_key:
            return "closeai"
        return "deepseek"

    @property
    def llm_api_key(self) -> str:
        if self.resolved_llm_provider == "closeai":
            return self.closeai_api_key
        return self.deepseek_api_key

    @property
    def llm_base_url(self) -> str:
        if self.resolved_llm_provider == "closeai":
            return self.closeai_base_url
        return self.deepseek_base_url

    @property
    def llm_model(self) -> str:
        return self.deepseek_model

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
