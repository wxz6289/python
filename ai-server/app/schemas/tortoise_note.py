from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str | None = None


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str | None
    created_at: datetime

class UserCreate(BaseModel):
    email: str = Field(min_length=1, max_length=20)
    username: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=1, max_length=20)

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    created_at: datetime
