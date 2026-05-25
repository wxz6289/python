from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app import __version__, Master, get_settings, close_db_engine, close_tortoise_orm, init_tortoise_orm, register_exception_handlers, UnifiedResponseMiddleware, ResponseCleanupMiddleware, add_process_time_header, install_unified_openapi, depend, devtools, learn, path, tortoise_demo, ws, chat_router, catalog_router, auth_router

def request_logger(request: Request):
    print(request.method, request.url)
    return None


def create_app(
    *,
    init_master: bool = True,
    init_db: bool = True,
    init_tortoise: bool | None = None,
) -> FastAPI:
    tortoise_enabled = init_db if init_tortoise is None else init_tortoise

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        devtools.ensure_devtools_json()
        if init_db:
            from app.db.session import get_engine

            get_engine()
        if tortoise_enabled:
            await init_tortoise_orm()
        app.state.master = Master(get_settings()) if init_master else None
        yield
        if tortoise_enabled:
            await close_tortoise_orm()
        if init_db:
            await close_db_engine()

    app = FastAPI(
        title="ai-server",
        description="FastAPI + LangChain + Redis 对话服务（RBAC + ACL）",
        version="0.2.0",
        dependencies=[Depends(request_logger)],
        lifespan=lifespan,
    )
    app.add_middleware(UnifiedResponseMiddleware)
    app.add_middleware(ResponseCleanupMiddleware)
    app.middleware("http")(add_process_time_header)
    register_exception_handlers(app)
    install_unified_openapi(app)

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(catalog_router)
    app.include_router(path.router)
    app.include_router(depend.router)
    learn.register_middlewares(app)
    app.include_router(learn.router, prefix="/v2", tags=["learn"])
    app.include_router(ws.router)
    app.include_router(tortoise_demo.router)
    app.include_router(devtools.router)
    app.mount("/resources", StaticFiles(directory="resources"), name="resources")

    return app


app = create_app()
print(f"ai-server version: {__version__}")
