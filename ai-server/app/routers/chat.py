from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.dependencies import get_master
from app.services.master import Master

router = APIRouter(tags=["chat"])


@router.get("/chat", response_class=PlainTextResponse)
def chat(
    query: str,
    session_id: str = "default",
    master: Master = Depends(get_master),
) -> str:
    """命理对话接口，返回纯文本。阻塞调用在线程池执行，避免阻塞事件循环。"""
    return master.chat(query, session_id)
