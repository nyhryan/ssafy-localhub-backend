from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.posts import (
    PostCreate,
    PostListItem,
    PostListResponse,
    PostRead,
    PostUpdate,
    PostVerifyRequest,
)
from app.services import posts as post_service

router = APIRouter(tags=["posts"])


def _to_post_read(post):
    category_name = None
    if getattr(post, "categories", None) is not None:
        category_name = getattr(post.categories, "name", None)

    return PostRead(
        id=post.id,
        title=post.title,
        content=post.content,
        image_path=post.image_path,
        views=post.views,
        likes=post.likes,
        created_at=post.created_at,
        updated_at=post.updated_at,
        category_name=category_name,
    )


@router.get("/posts/recent", response_model=list[PostListItem])
def get_recent_posts(
    db: Session = Depends(get_db),
    limit: int = Query(default=5, ge=1, le=20),
):
    posts = post_service.get_recent_posts(db=db, limit=limit)
    return [_to_post_read(post) for post in posts]


@router.get("/posts", response_model=PostListResponse)
def get_posts(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    keyword: str | None = Query(default=None),
):
    total, total_pages, posts = post_service.get_posts(
        db=db,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        keyword=keyword,
    )

    return PostListResponse(
        items=[_to_post_read(post) for post in posts],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/posts/{post_id}", response_model=PostRead)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = post_service.get_post(db=db, post_id=post_id)
    return _to_post_read(post)


@router.post("/posts", response_model=PostRead, status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    post = post_service.create_post(db=db, payload=payload)
    return _to_post_read(post)


@router.post("/posts/{post_id}/verify")
def verify_post_password(
    post_id: int,
    payload: PostVerifyRequest,
    db: Session = Depends(get_db),
):
    verified = post_service.verify_post_password(
        db=db,
        post_id=post_id,
        password=payload.password,
    )

    if not verified:
        return Response(status_code=401)
    else:
        return Response(status_code=200)


@router.put("/posts/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
):
    post = post_service.update_post(db=db, post_id=post_id, payload=payload)
    return _to_post_read(post)


@router.delete("/posts/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post_service.delete_post(db=db, post_id=post_id)
    return Response(status_code=204)