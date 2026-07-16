from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.models import Post

# ================================================================
# REQUEST DTO
# ================================================================

class PostCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)
    image_path: str | None = None
    category_name: str = Field(min_length=1)


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    image_path: str | None = None
    category_name: str = Field(min_length=1)


class PostPasswordVerify(BaseModel):
    password: str = Field(min_length=1)

class PostLikeToggle(BaseModel):
    has_liked:bool

# ================================================================
# RESPONSE DTO
# ================================================================

class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    image_path: str | None
    views: int
    likes: int
    created_at: datetime
    updated_at: datetime
    category_name: str | None = None

    @classmethod
    def from_post(cls, post: "Post") -> "PostResponse":
        category_name = None
        if getattr(post, "categories", None) is not None:
            category_name = getattr(post.categories, "name", None)
        return cls(
            id=post.id,
            title=post.title,
            content=post.content,
            image_path=post.image_path,
            views=post.views,
            likes=post.likes,
            created_at=post.created_at,
            updated_at=post.updated_at,
            category_name=category_name
        )


class PostListItem(PostResponse):
    pass


class PostListResponse(BaseModel):
    items: list[PostResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class PostLikeCountResponse(BaseModel):
    likes: int