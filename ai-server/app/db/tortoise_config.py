"""Tortoise ORM 与 MySQL 的初始化配置（含 Aerich 迁移配置）。"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from tortoise import Tortoise

from app.infra.compose import get_mysql_compose_config

TORTOISE_MODEL_MODULES = ["app.db.tortoise_models"]

# Aerich CLI 会 import 本模块，需避免依赖 get_settings()（会校验 DEEPSEEK_API_KEY）
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def build_tortoise_db_url() -> str:
    mysql = get_mysql_compose_config()
    host = os.getenv("MYSQL_HOST", str(mysql["host"]))
    port = int(os.getenv("MYSQL_PORT", str(mysql["port"])))
    user = os.getenv("MYSQL_USER", str(mysql["user"]))
    password = os.getenv("MYSQL_PASSWORD", str(mysql["password"]))
    database = os.getenv("MYSQL_DATABASE", str(mysql["database"]))
    password_encoded = quote_plus(password)
    return f"mysql://{user}:{password_encoded}@{host}:{port}/{database}"


TORTOISE_ORM = {
    "connections": {"default": build_tortoise_db_url()},
    "apps": {
        "models": {
            "models": [*TORTOISE_MODEL_MODULES, "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_tortoise_orm() -> None:
    # FastAPI lifespan 在后台 task 运行，请求在另一 task；需全局 fallback 才能跨 task 访问连接
    await Tortoise.init(
        config=TORTOISE_ORM,
        _enable_global_fallback=True,
    )


async def close_tortoise_orm() -> None:
    await Tortoise.close_connections()
