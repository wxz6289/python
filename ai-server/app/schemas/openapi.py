"""将 OpenAPI 成功响应 schema 统一包装为 ApiResponse 结构。"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.schemas.response import ResponseMeta

SKIP_PATH_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/resources")
SUCCESS_STATUS_CODES = frozenset({"200", "201", "202", "204"})


def _is_wrapped_schema(schema: dict[str, Any]) -> bool:
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return False
    return {"code", "msg", "data"}.issubset(properties)


def _wrap_data_schema(schema: dict[str, Any]) -> dict[str, Any]:
    if not schema:
        return {"type": "null"}

    wrapped = deepcopy(schema)
    if schema.get("type") == "null":
        return wrapped
    if "anyOf" in schema or "oneOf" in schema or "allOf" in schema:
        return wrapped
    if schema.get("type") == "array" or "items" in schema:
        return wrapped
    if "$ref" in schema:
        return wrapped
    return wrapped


def build_unified_response_schema(data_schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "title": "UnifiedApiResponse",
        "properties": {
            "code": {
                "type": "integer",
                "default": 0,
                "title": "Code",
            },
            "msg": {
                "type": "string",
                "default": "success",
                "title": "Msg",
            },
            "data": _wrap_data_schema(data_schema),
            "meta": {
                "anyOf": [
                    {"$ref": "#/components/schemas/ResponseMeta"},
                    {"type": "null"},
                ],
                "title": "Meta",
            },
        },
        "required": ["code", "msg", "data"],
    }


def _wrap_openapi_paths(schema: dict[str, Any]) -> None:
    paths = schema.get("paths", {})
    for path, path_item in paths.items():
        if path in SKIP_PATH_PREFIXES or path.startswith(SKIP_PATH_PREFIXES):
            continue
        if path.startswith("/ws"):
            continue

        for method, operation in path_item.items():
            if method not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue

            responses = operation.get("responses", {})
            for status_code, response in responses.items():
                if status_code not in SUCCESS_STATUS_CODES:
                    continue

                content = response.get("content", {})
                json_content = content.get("application/json")
                if not json_content:
                    continue

                inner_schema = json_content.get("schema", {})
                if _is_wrapped_schema(inner_schema):
                    continue

                json_content["schema"] = build_unified_response_schema(inner_schema)


def install_unified_openapi(app: FastAPI) -> None:
    """安装 OpenAPI 生成器：文档中的 JSON 成功响应统一为 {code, msg, data, meta?}。"""

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema is not None:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )

        components = schema.setdefault("components", {}).setdefault("schemas", {})
        components.setdefault(
            "ResponseMeta",
            ResponseMeta.model_json_schema(ref_template="#/components/schemas/{model}"),
        )
        _wrap_openapi_paths(schema)
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
