from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    description: str
    price: float = Field(ge=0)
