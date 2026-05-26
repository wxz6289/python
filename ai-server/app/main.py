from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles


def _make_lifespan(
    *,
    init_master: bool,
    init_db: bool,
    tortoise_enabled: bool,
):
    from app.chat.infrastructure.master import Master
    from app.config import get_settings
    from app.db.session import close_db_engine
    from app.db.tortoise_config import close_tortoise_orm, init_tortoise_orm
    from app.demo import devtools

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if init_db:
            from app.db.session import get_engine

            get_engine()
        if tortoise_enabled:
            await init_tortoise_orm()

        app.state.master = Master(get_settings()) if init_master else None
        try:
            yield
        finally:
            if tortoise_enabled:
                await close_tortoise_orm()
            if init_db:
                await close_db_engine()
            devtools.ensure_devtools_json()

    return lifespan


def _register_middlewares(app: FastAPI) -> None:
    from app.demo import learn
    from app.handlers import register_exception_handlers
    from app.middleware.response import UnifiedResponseMiddleware
    from app.middleware.response_cleanup import ResponseCleanupMiddleware
    from app.schemas.openapi import install_unified_openapi

    app.add_middleware(UnifiedResponseMiddleware)
    app.add_middleware(ResponseCleanupMiddleware)
    register_exception_handlers(app)
    install_unified_openapi(app)
    learn.register_middlewares(app)


def _register_routers(app: FastAPI) -> None:
    from app.auth.interface.router import router as auth_router
    from app.catalog.interface.router import router as catalog_router
    from app.chat.interface.router import router as chat_router
    from app.demo import depend, devtools, learn, path, tortoise_demo, ws
    from app.system.interface.router import router as system_router

    for router in (
        system_router,
        auth_router,
        chat_router,
        catalog_router,
        path.router,
        depend.router,
        ws.router,
        tortoise_demo.router,
        devtools.router,
    ):
        app.include_router(router)
    app.include_router(learn.router, prefix="/v2", tags=["learn"])


def create_app(
    *,
    init_master: bool = True,
    init_db: bool = True,
    init_tortoise: bool | None = None,
) -> FastAPI:
    from app.middleware.request_logger import request_logger

    tortoise_enabled = init_db if init_tortoise is None else init_tortoise

    app = FastAPI(
        title="ai-server",
        description="FastAPI + LangChain + Redis 对话服务（RBAC + ACL）",
        version="1.0.0",
        dependencies=[Depends(request_logger)],
        lifespan=_make_lifespan(
            init_master=init_master,
            init_db=init_db,
            tortoise_enabled=tortoise_enabled,
        ),
    )
    _register_middlewares(app)
    _register_routers(app)
    app.mount("/resources", StaticFiles(directory="resources"), name="resources")
    return app


app = create_app()
