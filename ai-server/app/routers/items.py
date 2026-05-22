from fastapi import APIRouter

from app.schemas.item import Item

router = APIRouter(prefix="/items", tags=["items"])


@router.post("")
async def create_item(item: Item) -> Item:
    """Pydantic 校验示例接口。"""
    return item
