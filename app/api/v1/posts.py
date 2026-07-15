from typing import List

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.posts import (
    PostCreate,
    PostListResponse,
    PostResponse,
    PostUpdate,
    PostPasswordVerify,
    PostLikeToggle,
    PostLikeCountResponse
)
from app.services import posts as post_service

router = APIRouter(tags=["posts"])


@router.get(
        "/posts/recent",
        response_model=List[PostResponse],
        summary="최근 게시물 조회(기본 5개)",
)
def get_recent_posts(
    db: Session = Depends(get_db),
    limit: int = Query(default=5, ge=1, le=20),
):
    posts = post_service.get_recent_posts(db=db, limit=limit)
    return [PostResponse.from_post(post) for post in posts]


@router.get("/posts", response_model=PostListResponse)
def get_posts(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    keyword: str | None = Query(default=None, description="제목과 본문에서 검색할 단어"),
    category: str | None = Query(default=None, description="카테고리(관광지, 문화시설,축제공연행사, 여행코스, 레포츠, 숙박, 쇼핑, 음식점)"),
):
    total, total_pages, posts = post_service.get_posts(
        db=db,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        keyword=keyword,
        category=category,
    )

    return PostListResponse(
        items=[PostResponse.from_post(post) for post in posts],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = post_service.get_post(db=db, post_id=post_id)
    return PostResponse.from_post(post)


@router.post("/posts", response_model=PostResponse, status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    post = post_service.create_post(db=db, payload=payload)
    return PostResponse.from_post(post)


@router.post("/posts/{post_id}/verify")
def verify_post_password(
    post_id: int,
    payload: PostPasswordVerify,
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


@router.put("/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
):
    post = post_service.update_post(db=db, post_id=post_id, payload=payload)
    return PostResponse.from_post(post)


@router.delete("/posts/{post_id}", status_code=204)
def delete_post(
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
def like_post(
    post_id: int,
    payload: PostLikeToggle,
    db: Session = Depends(get_db),
):
    like_count = post_service.update_post_like_count(db=db, post_id=post_id, payload=payload)
    return PostLikeCountResponse(likes=like_count)