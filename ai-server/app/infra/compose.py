"""从项目根目录 docker-compose.yml 读取基础设施配置。"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"


def _parse_env(items: list[Any] | dict[str, str] | None) -> dict[str, str]:
    if items is None:
        return {}
    if isinstance(items, dict):
        return {str(key): str(value) for key, value in items.items()}
    result: dict[str, str] = {}
    for item in items:
        if isinstance(item, str) and "=" in item:
            key, value = item.split("=", 1)
            result[key] = value
        elif isinstance(item, dict):
            result.update({str(key): str(value) for key, value in item.items()})
    return result


def _parse_host_port(ports: list[str | int] | None, default: int) -> int:
    if not ports:
        return default
    mapping = str(ports[0])
    if ":" in mapping:
        return int(mapping.split(":")[0])
    return int(mapping)


@lru_cache
def load_compose_service(service_name: str) -> dict[str, Any]:
    if not COMPOSE_FILE.exists():
        return {}
    data = yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8")) or {}
    services = data.get("services", {})
    service = services.get(service_name, {})
    return service if isinstance(service, dict) else {}


@lru_cache
def get_mysql_compose_config() -> dict[str, str | int]:
    mysql = load_compose_service("mysql")
    env = _parse_env(mysql.get("environment"))
    database = env.get("MYSQL_DATABASE") or env.get("MYSQL_ROOT") or "ai_server"
    return {
        "host": "127.0.0.1",
        "port": _parse_host_port(mysql.get("ports"), 3306),
        "user": "root",
        "password": env.get("MYSQL_ROOT_PASSWORD", ""),
        "database": database,
    }


@lru_cache
def get_redis_compose_config() -> dict[str, str | int]:
    redis = load_compose_service("bitnami_redis")
    env = _parse_env(redis.get("environment"))
    port = _parse_host_port(redis.get("ports"), 6379)
    password = env.get("REDIS_PASSWORD", "")
    auth = f":{password}@" if password else ""
    return {
        "host": "127.0.0.1",
        "port": port,
        "password": password,
        "url": f"redis://{auth}127.0.0.1:{port}/1",
    }
