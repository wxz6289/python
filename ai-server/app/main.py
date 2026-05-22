from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.routers import chat, items, ws
from app.services.master import Master


def create_app(*, init_master: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.master = Master(get_settings()) if init_master else None
        yield

    app = FastAPI(
        title="ai-server",
        description="FastAPI + LangChain + Redis 对话服务",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(chat.router)
    app.include_router(items.router)
    app.include_router(ws.router)

    return app


app = create_app()
