from pydantic import BaseModel, Field


class ChatQuery(BaseModel):
    query: str = Field(min_length=1, description="用户问题")
    session_id: str = Field(default="default", description="会话 ID，用于 Redis 多轮记忆")
