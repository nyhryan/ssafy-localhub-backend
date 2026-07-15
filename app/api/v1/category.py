# app/api/v1/category.py (에러 예외 처리 반영 버전)
from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db  
from app.models import POIItem, ContentType
from app.schemas.category import CategoryResponseSchema 
from app.services import category

router = APIRouter()

@router.get("/categories", response_model=CategoryResponseSchema)
def get_category_places(
    filter: str | None = Query(
        default=None,
        description="카테고리 명 입력(예: 관광지, 음식점, 쇼핑)",
    ),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    db: Session = Depends(get_db),
):
    return category.get_category_places(
        db=db,
        filter=filter,
        page=page,
    )