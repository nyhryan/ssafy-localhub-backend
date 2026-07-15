from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Post
from app.schemas.posts import (
    PostCreate,
    PostListItem,
    PostListResponse,
    PostRead,
    PostUpdate,
    PostVerifyRequest,
    PostLikeCountRequest,
    PostLikeCountResponse
)
from app.services import posts as post_service

router = APIRouter(tags=["posts"])


def _to_post_read(post: Post):
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
async def get_recent_posts(
    db: Session = Depends(get_db),
    limit: int = Query(default=5, ge=1, le=20),
):
    posts = post_service.get_recent_posts(db=db, limit=limit)
    return [_to_post_read(post) for post in posts]


@router.get("/posts", response_model=PostListResponse)
async def get_posts(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    keyword: str | None = Query(default=None, description="제목과 본문에서 검색할 단어"),
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
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = post_service.get_post(db=db, post_id=post_id)
    return _to_post_read(post)


@router.post("/posts", response_model=PostRead, status_code=201)
async def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    post = post_service.create_post(db=db, payload=payload)
    return _to_post_read(post)


@router.post("/posts/{post_id}/verify")
async def verify_post_password(
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
async def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
):
    post = post_service.update_post(db=db, post_id=post_id, payload=payload)
    return _to_post_read(post)


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post_service.delete_post(db=db, post_id=post_id)
    return Response(status_code=204)

@router.post(
    "/posts/{post_id}/like", 
    response_model=PostLikeCountResponse,
    summary="좋아요 수 업데이트",
    description="좋아요 수를 업데이트합니다. 사용자가 좋아요를 눌렀는지 여부를 localStorage에 저장한 것을 사용합니다. 현재 눌러진 상태라면 localStorage에 true, 백엔드 API에 요청을 보내면 좋아요를 하나 감소 시킵니다."
)
async def like_post(
    post_id: int,
    payload: PostLikeCountRequest,
    db: Session = Depends(get_db),
):
    like_count = post_service.update_post_like_count(db=db, post_id=post_id, payload=payload)
    return PostLikeCountResponse(likes=like_count)