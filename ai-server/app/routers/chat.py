from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import get_auth_service, get_current_user
from app.auth.schemas import UserRead
from app.auth.service import AuthorizationService
from app.dependencies import get_master
from app.services.master import Master

router = APIRouter(tags=["chat"])


async def prepare_chat_access(
    request: Request,
    current_user: UserRead = Depends(get_current_user),
    auth_service: AuthorizationService = Depends(get_auth_service),
) -> UserRead:
    session_id = request.query_params.get("session_id", "default")
    chat_session = await auth_service.get_chat_session(session_id)
    owner_id = chat_session.owner_id if chat_session else current_user.id
    resource_attrs = {
        "id": session_id,
        "owner_id": owner_id,
        "department": (
            chat_session.department
            if chat_session and chat_session.department
            else current_user.department
        ),
    }
    allowed = await auth_service.authorize(
        user_id=current_user.id,
        resource="chat",
        action="read",
        resource_type="chat_session",
        resource_id=session_id,
        resource_attrs=resource_attrs,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )

    await auth_service.ensure_chat_session(
        session_id=session_id,
        owner_id=owner_id,
        department=current_user.department,
    )
    return current_user


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
