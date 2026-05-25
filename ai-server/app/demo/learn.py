import time
from collections.abc import Awaitable, Callable
from urllib.parse import urlparse

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

router = APIRouter(prefix="/learn", tags=["learn"])

LEARN_CORS_ORIGINS = frozenset({
    "http://127.0.0.1:5500",
    "http://localhost:5500",
})

LEARN_CORS_HEADERS = {
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "*",
    "Vary": "Origin",
}

_DEFAULT_PORTS = {"http": 80, "https": 443}


def _origin_with_port(origin: str, referer: str = "") -> str:
    if not origin:
        return ""

    parsed = urlparse(origin)
    if not parsed.scheme or not parsed.hostname:
        return origin
    if parsed.port is not None:
        return origin

    referer_port = urlparse(referer).port if referer else None
    port = referer_port or _DEFAULT_PORTS[parsed.scheme]
    return f"{parsed.scheme}://{parsed.hostname}:{port}"


def _expand_cors_origins(origins: frozenset[str]) -> list[str]:
    """CORSMiddleware 精确匹配 Origin；浏览器可能省略端口，需同时允许带/不带端口。"""
    expanded: set[str] = set(origins)
    for origin in origins:
        parsed = urlparse(origin)
        if parsed.scheme and parsed.hostname:
            expanded.add(f"{parsed.scheme}://{parsed.hostname}")
            expanded.add(_origin_with_port(origin))
    return sorted(expanded)


LEARN_CORS_ORIGIN_LIST = _expand_cors_origins(LEARN_CORS_ORIGINS)


def _set_request_header(request: Request, name: str, value: str) -> None:
    name_bytes = name.lower().encode()
    value_bytes = value.encode()
    headers = [
        (header, val if header.lower() != name_bytes else value_bytes)
        for header, val in request.scope["headers"]
    ]
    if not any(header.lower() == name_bytes for header, _ in request.scope["headers"]):
        headers.append((name_bytes, value_bytes))
    request.scope["headers"] = headers


async def inject_origin_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """补全 Origin：无 header 时从 Referer 取；有 header 但无端口时补上端口。"""
    referer = request.headers.get("referer", "")
    raw_origin = request.headers.get("origin", "")

    if raw_origin:
        origin = _origin_with_port(raw_origin, referer)
        if origin != raw_origin:
            _set_request_header(request, "origin", origin)
    elif referer:
        parsed = urlparse(referer)
        if parsed.scheme and parsed.netloc:
            _set_request_header(
                request,
                "origin",
                _origin_with_port(f"{parsed.scheme}://{parsed.netloc}", referer),
            )

    return await call_next(request)

async def add_process_time_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start_time = time.time()
    print("test1")
    response = await call_next(request)
    print("after call_next 1")
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


async def middleware2(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    print("test2")
    response = await call_next(request)
    print("after call_next 2")
    return response


async def middleware3(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    print("test3")
    response = await call_next(request)
    print("after call_next 3")
    return response


async def log_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    print(f"Request: {request.method} {request.url}")
    # print(f"Headers: {request.headers}")
    body = await request.body()
    print(f"Body: {body!r}")
    print(f"Query: {request.query_params}")
    return await call_next(request)

async def learn_cors_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """自定义 CORS 实现（学习用，已由 CORSMiddleware 接管）。"""
    if not request.url.path.startswith("/learn"):
        return await call_next(request)

    raw_origin = request.headers.get("origin", "")
    origin = _origin_with_port(raw_origin, request.headers.get("referer", ""))
    if origin not in LEARN_CORS_ORIGINS:
        return await call_next(request)

    cors_headers = {
        **LEARN_CORS_HEADERS,
        "Access-Control-Allow-Origin": origin or raw_origin,
    }

    if request.method == "OPTIONS":
        return Response(status_code=200, headers=cors_headers)

    response = await call_next(request)
    response.headers.update(cors_headers)
    return response


def register_middlewares(app: FastAPI) -> None:
    app.middleware("http")(add_process_time_header)
    app.middleware("http")(middleware2)
    app.middleware("http")(middleware3)
    app.middleware("http")(log_request)
    # app.middleware("http")(learn_cors_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=LEARN_CORS_ORIGIN_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(inject_origin_middleware)


@router.get("")
async def learn() -> dict[str, str]:
    return {"message": "Hello, World!"}
