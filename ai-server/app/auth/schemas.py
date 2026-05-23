from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    user_id: int


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    email: str | None = None
    department: str | None = None


class UserRead(BaseModel):
    id: int
    username: str
    email: str | None = None
    department: str | None = None
    roles: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class PermissionCheckRequest(BaseModel):
    resource: str
    action: str
    resource_type: str | None = None
    resource_id: str | None = None
    resource_attrs: dict[str, object] = Field(default_factory=dict)


class PermissionCheckResponse(BaseModel):
    allowed: bool
