from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.infrastructure.models import Permission, Role, User, UserRole


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.username == username)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def user_has_permission(
    session: AsyncSession,
    user_id: int,
    resource: str,
    action: str,
) -> bool:
    stmt = (
        select(Permission.id)
        .join(Role.permissions)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
        .where(Permission.resource == resource)
        .where(or_(Permission.action == action, Permission.action == "*"))
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


def user_role_codes(user: User) -> list[str]:
    return [role.code for role in user.roles]


def user_permission_codes(user: User) -> list[str]:
    codes: set[str] = set()
    for role in user.roles:
        for permission in role.permissions:
            codes.add(permission.code)
    return sorted(codes)
