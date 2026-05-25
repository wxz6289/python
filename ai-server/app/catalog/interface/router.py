import re
from typing import List, Optional, Union

from fastapi import APIRouter, Query, status
from pydantic import Field

from app.catalog.schemas.item import Item
from app.schemas.response import page_meta, set_response_meta, set_response_msg

router = APIRouter(prefix="/items", tags=["items"])

MOCK_TOTAL = 100

# 与 query_items6 的 Query(pattern=...) 一致：三位数字-两位数字，如 123-45
_QUERY6_PATTERN = re.compile(r"^(?P<first>\d{3})-(?P<last>\d{2})$")


def _mock_item(item_id: int) -> Item:
    return Item(
        name=f"Item {item_id}",
        description=f"Item description {item_id}",
        price=100.00 if item_id % 2 == 0 else 0.00,
    )


@router.post("", status_code=status.HTTP_200_OK)
async def create_item(item: Item) -> Item:
    """Pydantic 校验示例接口。"""
    set_response_msg("created")
    return item


@router.get("/v1")
async def get_items(page: int = 1, page_size: int = 10) -> list[Item]:
    """获取分页物品。"""
    if page < 1 or page_size < 1:
        page = max(page, 1)
        page_size = max(page_size, 1)

    start = (page - 1) * page_size
    end = min(start + page_size, MOCK_TOTAL)
    items = [_mock_item(i + 1) for i in range(start, end)]
    set_response_meta(page_meta(page=page, page_size=page_size, total=MOCK_TOTAL))
    return items


@router.get("/v2/{item_id}")
async def get_item(item_id: int, q: str | None = None) -> dict[str, Item | str | None]:
    """获取单个物品。"""
    return {"item": _mock_item(item_id), "q": q}


@router.get("/test/${id}")
async def get_item_by_id(id: Union[int, str]):
    return {"id": id}


# 路径参数必传
@router.get("/test0")
@router.get("/test0/${id}")
async def get_item_by_id0(id: Optional[int] = None):
    if id is None:
        return {"id": "default"}
    else:
        return {"id": id}


@router.get("/test1/")
async def get_item_by_id1(id: Union[int, str, None] = None):
    return {"id": id}


@router.get("/test2/")
async def get_item_by_id2(id: Optional[int] = None):
    return {"id": id}


# 列表多态参数不能放在路径上
@router.get("/test3/")
async def get_item_by_id3(ids: List[int]):
    return {"id": id}


@router.get("/query/q")
async def query_items(q: Optional[str] = Query(None)):
    return {"q": q}


@router.get("/query1/q")
async def query_items1(q: Optional[str] = Query(...)):
    return {"q": q}


@router.get("/query2/q")
async def query_items2(q: Optional[str] = Query(..., max_length=6, min_length=2)):
    return {"q": q}


@router.get("/query3/q")
async def query_items3(q: int = Query(..., gt=6, le=10)):
    return {"q": q}


@router.get("/query4/q")
async def query_items4(
    q: int = Query(..., gt=6, le=10, alias="id", description="ID of the item to update")
):
    return {"q": q}


@router.get("/query5/q")
async def query_items5(q: int = Query(..., ge=6, le=10, deprecated=True)):
    return {"q": q}


@router.get("/query6/q")
async def query_items6(q: str = Query(..., pattern=r"^\d{3}-\d{2}$")):
    """Query 校验格式后，用命名分组提取 first / last。"""
    match = _QUERY6_PATTERN.fullmatch(q)
    if match is None:
        # FastAPI 已校验 pattern，正常请求不会走到这里
        return {"q1": None, "q2": None}
    return {"q1": match.group("first"), "q2": match.group("last")}


@router.put("/{item_id}")
async def update_item(item_id: int, item: Item) -> Item:
    """更新单个物品。"""
    return item.model_copy(update={"name": item.name or f"Item {item_id}"})


@router.delete("/{item_id}")
async def delete_item(item_id: int) -> None:
    """删除单个物品。"""
    set_response_msg(f"item {item_id} deleted")


class ItemOut(Item):
    price: float = Field(ge=0, description="Item price")
    items: list[int]| None = Field(default=None, description="Item items")

@router.get("/query7/q", response_model=ItemOut, response_model_exclude_unset=True)
async def query_items7(q: str):
    return ItemOut(name=q, description="Item description", price=100.00)
