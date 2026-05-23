from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.response import fail


def _validation_error_message(errors: list[dict[str, Any]]) -> str:
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


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
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

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        body = fail(
            code=422,
            msg=_validation_error_message(exc.errors()),
        )
        return JSONResponse(status_code=422, content=body.serialize_model())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        body = fail(code=500, msg="Internal server error")
        return JSONResponse(status_code=500, content=body.serialize_model())
