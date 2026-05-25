from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.schemas.response import (
    ApiResponse,
    bind_request,
    get_response_meta,
    get_response_msg,
    normalize_response_data,
    unbind_request,
)

SKIP_PATH_PREFIXES = (
    "/docs",
    "/redoc",
    "/openapi.json",
    "/.well-known",
)


def _should_skip(request: Request, response: Response) -> bool:
    path = request.url.path
    if path in SKIP_PATH_PREFIXES or path.startswith(SKIP_PATH_PREFIXES):
        return True
    if path.startswith("/ws") or request.scope.get("type") == "websocket":
        return True
    content_type = response.headers.get("content-type", "")
    return "application/json" not in content_type


def _is_already_wrapped(payload: Any) -> bool:
    return isinstance(payload, dict) and "code" in payload and "msg" in payload


class UnifiedResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        token = bind_request(request)
        try:
            response = await call_next(request)
            if _should_skip(request, response):
                return response

            body = b"".join([chunk async for chunk in response.body_iterator])
            if not body:
                payload: Any = None
            else:
                payload = json.loads(body)

            if _is_already_wrapped(payload):
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type="application/json",
                )

            wrapped: ApiResponse[Any] = ApiResponse(
                code=0,
                msg=get_response_msg(request),
                data=normalize_response_data(payload),
                meta=get_response_meta(request),
            )
            headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower() != "content-length"
            }
            return JSONResponse(
                content=wrapped.serialize_model(),
                status_code=response.status_code,
                headers=headers,
            )
        finally:
            unbind_request(token)
