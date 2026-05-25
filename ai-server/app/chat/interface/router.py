from fastapi import APIRouter, Depends

from app.auth.interface.schemas import UserRead
from app.chat.application.access import prepare_chat_access
from app.chat.infrastructure.master import Master
from app.chat.interface.dependencies import get_master

router = APIRouter(tags=["chat"])


@router.get("/chat")
def chat(
    query: str,
    session_id: str = "default",
    _: UserRead = Depends(prepare_chat_access),
    master: Master = Depends(get_master),
) -> dict[str, str]:
    """命理对话接口。需 RBAC + ACL 授权。"""
    reply = master.chat(query, session_id)
    return {"reply": reply, "session_id": session_id}
