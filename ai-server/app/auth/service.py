from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.acl import AuthContext, evaluate_acl_entries, fetch_acl_entries
from app.auth.models import ChatSession, User
from app.auth.rbac import get_user_by_id, user_has_permission, user_role_codes


class AuthorizationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_context(self, user_id: int) -> dict[str, Any] | None:
        user = await get_user_by_id(self.session, user_id)
        if user is None or user.status != 1:
            return None
        return {
            "id": user.id,
            "username": user.username,
            "department": user.department,
            "roles": user_role_codes(user),
            "role_ids": [role.id for role in user.roles],
        }

    async def authorize(
        self,
        *,
        user_id: int,
        resource: str,
        action: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        resource_attrs: dict[str, Any] | None = None,
    ) -> bool:
        user_ctx = await self.get_user_context(user_id)
        if user_ctx is None:
            return False

        if not await user_has_permission(self.session, user_id, resource, action):
            return False

        acl_resource_type = resource_type or resource
        acl_resource_id = resource_id or "*"
        entries = await fetch_acl_entries(
            self.session,
            user_id=user_id,
            role_ids=user_ctx["role_ids"],
            resource_type=acl_resource_type,
            resource_id=acl_resource_id,
            action=action,
        )

        ctx = AuthContext(
            user=user_ctx,
            resource={
                "type": acl_resource_type,
                "id": acl_resource_id,
                **(resource_attrs or {}),
            },
            env={"hour": datetime.now().hour},
        )
        acl_result = evaluate_acl_entries(entries, ctx)
        if acl_result is None:
            return True
        return acl_result

    async def ensure_chat_session(
        self,
        *,
        session_id: str,
        owner_id: int,
        department: str | None,
    ) -> ChatSession:
        stmt = select(ChatSession).where(ChatSession.session_id == session_id)
        result = await self.session.execute(stmt)
        chat_session = result.scalar_one_or_none()
        if chat_session is None:
            chat_session = ChatSession(
                session_id=session_id,
                owner_id=owner_id,
                department=department,
            )
            self.session.add(chat_session)
            await self.session.commit()
            await self.session.refresh(chat_session)
        return chat_session

    async def get_chat_session(self, session_id: str) -> ChatSession | None:
        stmt = select(ChatSession).where(ChatSession.session_id == session_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        *,
        username: str,
        password_hash: str,
        email: str | None = None,
        department: str | None = None,
    ) -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            email=email,
            department=department,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
