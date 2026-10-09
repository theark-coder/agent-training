from typing import Literal

from pydantic import BaseModel, Field


# 用户请求与响应
class UserCreate(BaseModel):
    id: int = Field(gt=0, strict=True)
    name: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: int
    name: str
    role: str


# 会话请求与响应
class ConversationCreate(BaseModel):
    user_id: int = Field(gt=0, strict=True)
    title: str = Field(min_length=1, max_length=200)


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str | None


# 消息请求与响应
class MessageCreate(BaseModel):
    conversation_id: int = Field(gt=0, strict=True)
    role: Literal["user", "assistant", "system"]
    content: str = Field(min_length=1)


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str