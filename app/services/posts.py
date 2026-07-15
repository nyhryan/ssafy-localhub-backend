from math import ceil

from fastapi import HTTPException
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.models import ContentType, Post
from app.schemas.posts import PostCreate, PostUpdate


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
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


def get_posts(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
):
    query = db.query(Post).outerjoin(ContentType, Post.category_id == ContentType.contentTypeId)

    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Post.title.ilike(like_pattern),
                Post.content.ilike(like_pattern),
            )
        )

    total = query.count()
    total_pages = ceil(total / page_size) if total > 0 else 0

    items = (
        query.order_by(_get_sort_expression(sort_by, sort_order))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return total, total_pages, items


def get_recent_posts(db: Session, limit: int = 5):
    return (
        db.query(Post)
        .order_by(Post.created_at.desc(), Post.id.desc())
        .limit(limit)
        .all()
    )


def get_post(db: Session, post_id: int):
    return _get_post_or_404(db, post_id)


def create_post(db: Session, payload: PostCreate):
    category = (
        db.query(ContentType)
        .filter(ContentType.contentTypeId == payload.category_id)
        .first()
    )
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    post = Post(
        title=payload.title,
        content=payload.content,
        password=payload.password,
        image_path=payload.image_path,
        category_id=payload.category_id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def verify_post_password(db: Session, post_id: int, password: str) -> bool:
    post = _get_post_or_404(db, post_id)
    return post.password == password


def update_post(db: Session, post_id: int, payload: PostUpdate):
    post = _get_post_or_404(db, post_id)

    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content
    if payload.image_path is not None:
        post.image_path = payload.image_path
    if payload.category_id is not None:
        category = (
            db.query(ContentType)
            .filter(ContentType.contentTypeId == payload.category_id)
            .first()
        )
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        post.category_id = payload.category_id

    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int):
    post = _get_post_or_404(db, post_id)

    db.delete(post)
    db.commit()