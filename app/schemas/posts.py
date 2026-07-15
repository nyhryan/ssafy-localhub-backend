from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# ==== 애플리케이션 DTO 정의 ====

class PostCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)
    image_path: str | None = None
    category_id: str = Field(min_length=1)


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    image_path: str | None = None
    category_id: str | None = None


class PostVerifyRequest(BaseModel):
    password: str = Field(min_length=1)


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    image_path: str | None
    views: int
    likes: int
    created_at: datetime
    updated_at: datetime
    category_id: str
    category_name: str | None = None


class PostListItem(PostRead):
    pass


class PostListResponse(BaseModel):
    items: list[PostListItem]
    page: int
    page_size: int
    total: int
    total_pages: int