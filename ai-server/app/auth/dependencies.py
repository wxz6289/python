from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac import get_user_by_username, user_permission_codes, user_role_codes
from app.auth.schemas import UserRead
from app.auth.security import decode_access_token, verify_password
from app.auth.service import AuthorizationService
from app.db.session import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
) -> AuthorizationService:
    return AuthorizationService(session)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    username = payload.get("sub")
    if not isinstance(username, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_username(session, username)
    if user is None or user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        department=user.department,
        roles=user_role_codes(user),
    )


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> UserRead | None:
    user = await get_user_by_username(session, username)
    if user is None or user.status != 1:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        department=user.department,
        roles=user_role_codes(user),
    )


def require_permission(
    resource: str,
    action: str,
    *,
    resource_type: str | None = None,
    resource_id_getter: Callable[[Request], str | None] | None = None,
    resource_attrs_getter: Callable[[Request, UserRead], dict[str, Any]] | None = None,
):
    async def checker(
        request: Request,
        current_user: UserRead = Depends(get_current_user),
        auth_service: AuthorizationService = Depends(get_auth_service),
    ) -> UserRead:
        resolved_resource_id = (
            resource_id_getter(request) if resource_id_getter else None
        )
        resource_attrs = (
            resource_attrs_getter(request, current_user)
            if resource_attrs_getter
            else {}
        )
        allowed = await auth_service.authorize(
            user_id=current_user.id,
            resource=resource,
            action=action,
            resource_type=resource_type,
            resource_id=resolved_resource_id,
            resource_attrs=resource_attrs,
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        return current_user

    return checker


async def get_user_permissions(
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[str]:
    user = await get_user_by_username(session, current_user.username)
    if user is None:
        return []
    return user_permission_codes(user)
