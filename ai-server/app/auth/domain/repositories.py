from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.auth.infrastructure.models import AclEntry, ChatSession, User


class UserRepository(Protocol):
    async def get_by_id(self, user_id: int) -> User | None: ...

    async def get_by_username(self, username: str) -> User | None: ...

    async def save(self, user: User) -> User: ...


class PermissionRepository(Protocol):
    async def user_has_permission(
        self, user_id: int, resource: str, action: str
    ) -> bool: ...


class AclRepository(Protocol):
    async def fetch_entries(
        self,
        *,
        user_id: int,
        role_ids: list[int],
        resource_type: str,
        resource_id: str,
        action: str,
    ) -> list[AclEntry]: ...


class ChatSessionRepository(Protocol):
    async def get_by_session_id(self, session_id: str) -> ChatSession | None: ...

    async def ensure(
        self,
        *,
        session_id: str,
        owner_id: int,
        department: str | None,
    ) -> ChatSession: ...
