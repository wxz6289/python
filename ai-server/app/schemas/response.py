from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from starlette.requests import Request

T = TypeVar("T")

_current_request: ContextVar[Request | None] = ContextVar("current_request", default=None)


class ResponseMeta(BaseModel):
    page: int | None = None
    page_size: int | None = None
    total: int | None = None
    total_pages: int | None = None


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    msg: str = "success"
    data: T | None = None
    meta: ResponseMeta | None = None

    def serialize_model(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "msg": self.msg,
            "data": self.data,
        }
        if self.meta is not None:
            payload["meta"] = self.meta.model_dump(mode="json")
        return payload


def _resolve_request(request: Request | None = None) -> Request | None:
    return request or _current_request.get()


def set_response_meta(meta: ResponseMeta, request: Request | None = None) -> None:
    req = _resolve_request(request)
    if req is not None:
        req.state.response_meta = meta


def set_response_msg(msg: str, request: Request | None = None) -> None:
    req = _resolve_request(request)
    if req is not None:
        req.state.response_msg = msg


def get_response_meta(request: Request | None = None) -> ResponseMeta | None:
    req = _resolve_request(request)
    if req is None:
        return None
    return getattr(req.state, "response_meta", None)


def get_response_msg(request: Request | None = None) -> str:
    req = _resolve_request(request)
    if req is None:
        return "success"
    return getattr(req.state, "response_msg", None) or "success"


def bind_request(request: Request) -> Token:
    request.state.response_meta = None
    request.state.response_msg = None
    return _current_request.set(request)


def unbind_request(token: Token) -> None:
    _current_request.reset(token)


def page_meta(*, page: int, page_size: int, total: int) -> ResponseMeta:
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ResponseMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


def fail(
    *,
    code: int,
    msg: str,
    data: Any | None = None,
    meta: ResponseMeta | None = None,
) -> ApiResponse[Any]:
    return ApiResponse(code=code, msg=msg, data=data, meta=meta)
