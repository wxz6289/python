from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    authenticate_user,
    get_auth_service,
    get_current_user,
    get_user_permissions,
)
from app.auth.schemas import (
    PermissionCheckRequest,
    Token,
    UserCreate,
    UserRead,
)
from app.auth.security import create_access_token, hash_password
from app.auth.service import AuthorizationService
from app.db.session import get_db_session
from app.schemas.response import set_response_msg

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user_id=user.id, username=user.username)
    return Token(access_token=token)


@router.get("/me")
async def read_me(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    return current_user


@router.get("/permissions")
async def read_permissions(
    permissions: list[str] = Depends(get_user_permissions),
) -> list[str]:
    return permissions


@router.post("/check")
async def check_permission(
    body: PermissionCheckRequest,
    current_user: UserRead = Depends(get_current_user),
    auth_service: AuthorizationService = Depends(get_auth_service),
) -> bool:
    return await auth_service.authorize(
        user_id=current_user.id,
        resource=body.resource,
        action=body.action,
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        resource_attrs=body.resource_attrs,
    )


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    auth_service: AuthorizationService = Depends(get_auth_service),
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    user = await auth_service.create_user(
        username=body.username,
        password_hash=hash_password(body.password),
        email=body.email,
        department=body.department,
    )
    set_response_msg("created")
    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        department=user.department,
        roles=[],
    )
