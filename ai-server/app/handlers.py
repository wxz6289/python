from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from openai import AuthenticationError, PermissionDeniedError

from app.schemas.response import fail


def _validation_error_message(errors: Sequence[dict[str, Any]]) -> str:
    if not errors:
        return "Validation failed"

    first = errors[0]
    msg = str(first.get("msg", "Validation failed"))
    if msg.startswith("Value error, "):
        msg = msg.removeprefix("Value error, ")

    loc = first.get("loc", ())
    if loc:
        field = ".".join(str(part) for part in loc if part not in {"body", "query", "path"})
        if field:
            return f"{field}: {msg}"
    return msg


async def http_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, HTTPException):
        raise exc
    detail = exc.detail
    if isinstance(detail, dict):
        msg = str(detail.get("msg", detail))
    elif isinstance(detail, list):
        msg = "Request failed"
    else:
        msg = str(detail)

    body = fail(code=exc.status_code, msg=msg)
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=body.serialize_model(),
        headers=headers,
    )


async def validation_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise exc
    body = fail(
        code=422,
        msg=_validation_error_message(exc.errors()),
    )
    return JSONResponse(status_code=422, content=body.serialize_model())


async def llm_authentication_error_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, (AuthenticationError, PermissionDeniedError)):
        raise exc
    body = fail(
        code=502,
        msg=(
            "LLM API key is invalid. Check DEEPSEEK_API_KEY / CLOSEAI_API_KEY, "
            "LLM_PROVIDER, and DEEPSEEK_BASE_URL / CLOSEAI_BASE_URL in .env"
        ),
    )
    return JSONResponse(status_code=502, content=body.serialize_model())


async def unhandled_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    body = fail(code=500, msg="Internal server error")
    return JSONResponse(status_code=500, content=body.serialize_model())


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(AuthenticationError, llm_authentication_error_handler)
    app.add_exception_handler(PermissionDeniedError, llm_authentication_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
