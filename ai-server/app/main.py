from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.db.session import close_db_engine
from app.db.tortoise_config import close_tortoise_orm, init_tortoise_orm
from app.handlers import register_exception_handlers
from app.middleware.response import UnifiedResponseMiddleware
from app.routers import auth, chat, items, path, tortoise_demo, ws
from app.services.master import Master


def create_app(
    *,
    init_master: bool = True,
    init_db: bool = True,
    init_tortoise: bool | None = None,
) -> FastAPI:
    tortoise_enabled = init_db if init_tortoise is None else init_tortoise

    @asynccontextmanager
    async def lifespan(app: FastAPI):
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
        lifespan=lifespan,
    )
    app.add_middleware(UnifiedResponseMiddleware)
    register_exception_handlers(app)

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(chat.router)
    app.include_router(items.router)
    app.include_router(path.router)
    app.include_router(ws.router)
    app.include_router(tortoise_demo.router)
    app.mount("/resources", StaticFiles(directory="resources"), name="resources")

    return app


app = create_app()
