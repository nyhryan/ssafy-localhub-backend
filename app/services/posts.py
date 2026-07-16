from math import ceil
from typing import List

from fastapi import HTTPException
from sqlalchemy import asc, desc, func, or_, update, select
from sqlalchemy.orm import Session

from app.models import ContentType, Post
from app.schemas.posts import PostCreate, PostUpdate, PostLikeToggle


ALLOWED_SORT_FIELDS = {
    "id": Post.id,
    "created_at": Post.created_at,
    "updated_at": Post.updated_at,
    "views": Post.views,
    "likes": Post.likes,
}

def _get_sort_expression(sort_by: str, sort_order: str):
    sort_column = ALLOWED_SORT_FIELDS.get(sort_by, Post.created_at)
    return asc(sort_column) if sort_order.lower() == "asc" else desc(sort_column)

def _get_post_or_404(db: Session, post_id: int) -> Post:
    stmt = select(Post).where(Post.id == post_id)
    post = db.scalars(stmt).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

def _get_category_or_404(db: Session, category_name: str) -> ContentType:
    stmt = select(ContentType).where(ContentType.name == category_name)
    category = db.scalars(stmt).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

def get_posts(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
    category: str | None = None,
) -> tuple[int, int, list[Post]]:
    stmt = select(Post).outerjoin(ContentType, Post.category_id == ContentType.contentTypeId)

    if keyword:
        like_pattern = f"%{keyword}%"
        stmt = stmt.where(
            or_(
                Post.title.ilike(like_pattern),
                Post.content.ilike(like_pattern),
            )
        )
    
    if category:
        stmt = stmt.where(ContentType.name == category)
    
    subq = stmt.with_only_columns(Post.id).subquery()
    total = db.execute(
        select(func.count()).select_from(subq)
    ).scalar() or 0
    total_pages = ceil(total / page_size) if total > 0 else 0

    # Paginate and order
    stmt = (
        stmt.order_by(_get_sort_expression(sort_by, sort_order))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    
    items = list(db.scalars(stmt).all())

    return total, total_pages, items

def get_recent_posts(db: Session, limit: int = 5) -> List[Post]:
    stmt = (
        select(Post)
        .order_by(Post.created_at.desc(), Post.id.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())

def get_post(db: Session, post_id: int) -> Post:
    # Increment the view count for the post
    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(views=Post.views + 1)
    )
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    db.commit()

    return _get_post_or_404(db, post_id)


def create_post(db: Session, payload: PostCreate) -> Post:
    category = _get_category_or_404(db, payload.category_name)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    post = Post(
        title=payload.title,
        content=payload.content,
        password=payload.password,
        image_path=payload.image_path,
        category_id=category.contentTypeId,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def verify_post_password(db: Session, post_id: int, password: str) -> bool:
    post = _get_post_or_404(db, post_id)
    return post.password == password


def update_post(db: Session, post_id: int, payload: PostUpdate) -> Post:
    post = _get_post_or_404(db, post_id)

    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content
    if payload.image_path is not None:
        post.image_path = payload.image_path
    if payload.category_name is not None:
        category = _get_category_or_404(db, payload.category_name)
        post.category_id = category.contentTypeId

    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int):
    post = _get_post_or_404(db, post_id)

    db.delete(post)
    db.commit()

def update_post_like_count(db: Session, post_id: int, payload: PostLikeToggle) -> int:
    delta = -1 if payload.has_liked else 1

    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(likes=Post.likes + delta)
        .returning(Post.likes)
    )

    result = db.execute(stmt)
    likes = result.scalar_one_or_none()

    if likes is None:
        raise HTTPException(status_code=404, detail="Post not found")

    db.commit()
    return likes
