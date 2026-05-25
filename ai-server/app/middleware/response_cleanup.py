from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.middleware.response import SKIP_PATH_PREFIXES, _is_already_wrapped

PAGINATION_FIELDS = ("page", "page_size", "total", "total_pages")


def _should_skip(request: Request, response: Response) -> bool:
    path = request.url.path
    if path in SKIP_PATH_PREFIXES or path.startswith(SKIP_PATH_PREFIXES):
        return True
    if path.startswith("/ws") or request.scope.get("type") == "websocket":
        return True
    content_type = response.headers.get("content-type", "")
    return "application/json" not in content_type


def _has_pagination_meta(meta: Any) -> bool:
    if not isinstance(meta, dict):
        return False
    return any(meta.get(field) is not None for field in PAGINATION_FIELDS)


def _strip_none_values(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_none_values(item)
            for key, item in value.items()
            if item is not None
        }
    if isinstance(value, list):
        return [_strip_none_values(item) for item in value if item is not None]
    return value


def clean_api_response(payload: Any) -> Any:
    if not _is_already_wrapped(payload):
        return payload

    cleaned = dict(payload)
    meta = cleaned.get("meta")
    if meta is not None and not _has_pagination_meta(meta):
        cleaned.pop("meta", None)
    if "data" in cleaned and cleaned["data"] is not None:
        cleaned["data"] = _strip_none_values(cleaned["data"])
    return cleaned


class ResponseCleanupMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        if _should_skip(request, response):
            return response

        body = b"".join([chunk async for chunk in response.body_iterator])
        if not body:
            return response

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )

        cleaned = clean_api_response(payload)
        if cleaned == payload:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json",
            )

        headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() != "content-length"
        }
        return JSONResponse(
            content=cleaned,
            status_code=response.status_code,
            headers=headers,
        )
