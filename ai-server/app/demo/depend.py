from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.param_functions import Query
from pydantic import BaseModel, Field

from app.schemas.response import ResponseMeta, set_response_meta

def check_auth(token: str = Header(...)):
    if token != "secret-token":
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"role": "admin"}

router = APIRouter(prefix="/depend", tags=["depend"], dependencies=[Depends(check_auth)])


def get_query_params(q: str = Query(default="", description="Query string")):
    return q


def check_user_permission(token: str = Header(...)):
    if token != "secret-token":
        raise HTTPException(status_code=403, detail="Forbidden")
    return token

UserInfo = Annotated[dict[str, str], Depends(check_user_permission)]

def user_info(token: UserInfo):
    return {"role": "admin", "token": token}

def pagination_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> dict[str, int]:
    return {"page": page, "page_size": page_size}


QueryParams = Annotated[str, Depends(get_query_params)]
PaginationParams = Annotated[dict[str, int], Depends(pagination_params)]

class UserService:
    def __init__(self, connection: str = "default"):
        self.connection = connection

    def get_user_info(self, user_id: int) -> dict[str, str|int]:
        return {"role": "admin", "user_id": user_id, "connection": self.connection}

def get_user_service(connection: str = "default") -> UserService:
    return UserService(connection)


@router.get("")
async def depend_v1(query: QueryParams) -> dict[str, str]:
    return {"message": query}


@router.get("/v2", dependencies=[Depends(check_user_permission)])
async def depend_v2() -> dict[str, str]:
    return {"message": "depend_v2", "role": "admin"}


@router.get("/items")
async def get_items(pagination: PaginationParams) -> list[dict[str, object]]:
    total = 100
    start = pagination["page"] * pagination["page_size"] + 1
    end = (pagination["page"] + 1) * pagination["page_size"]

    items = [
        {"id": i, "name": f"Item {i}", "description": f"Item {i} description"}
        for i in range(start, end)
    ]

    meta = ResponseMeta(
        total=total,
        total_pages=total // pagination["page_size"],
        page=pagination["page"],
        page_size=pagination["page_size"],
    )
    set_response_meta(meta)
    return items

Info = Annotated[dict[str, str], Depends(user_info)]

@router.get("/user-info")
async def get_user_info(info: Info) -> dict[str, str]:
    return info

UserServiceType = Annotated[UserService, Depends(get_user_service)]

@router.get("/user-service")
async def get_user_service_test(user_id: int, user_service: UserServiceType) -> dict[str, str|int]:
    return user_service.get_user_info(user_id)
