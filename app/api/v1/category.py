# app/api/v1/categories.py
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

# 우리 DB 세션 가져오기 및 모델 가져오기 (경로가 다를 경우 임포트 경로 확인 필수!)
from app.database import get_db  
from app.models import POIItem, ContentType  # models.py 파일에서 직접 임포트

router = APIRouter()

# --- 1. 응답 데이터 명세서에 맞춘 Pydantic Schemas ---
class PlaceSchema(BaseModel):
    id: str
    title: str
    address: Optional[str] = None
    image: Optional[str] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None

    class Config:
        from_attributes = True  # SQLAlchemy 객체를 Pydantic으로 자동 변환해 줌

class PageInfoSchema(BaseModel):
    current_page: int
    total_pages: int
    total_items: int

class CategoryResponseSchema(BaseModel):
    places: List[PlaceSchema]
    pages: PageInfoSchema


# --- 2. API 엔드포인트 구현 ---
@router.get("/categories", response_model=CategoryResponseSchema)
def get_category_places(
    filter: Optional[str] = Query(None, description="카테고리 필터 (contentTypeId 값 입력)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    db: Session = Depends(get_db)  # 실제 DB 세션 주입
):
    # 1. POIItem 테이블 조회 쿼리 빌더 생성
    query = db.query(POIItem)
    
    # 2. 카테고리(contentTypeId) 필터링 조건 적용
    if filter:
        query = query.filter(POIItem.contenttypeid == filter)
        
    # 3. 페이지네이션 계산
    items_per_page = 10
    total_items = query.count()
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # 해당 페이지에 보여줄 데이터 슬라이싱 (.offset() 과 .limit() 활용)
    offset = (page - 1) * items_per_page
    db_places = query.offset(offset).limit(items_per_page).all()
    
    # 4. 명세서에 적힌 필드명과 DB 컬럼명이 매칭되도록 가공하여 전달
    result_places = []
    for place in db_places:
        result_places.append({
            "id": place.contentid,
            "title": place.title,
            "address": place.addr1,
            "image": place.firstimage2,  # DB의 firstimage2를 image 필드로 매핑
            "mapx": place.mapx,
            "mapy": place.mapy
        })
        
    # 5. 최종 규격 데이터 반환
    return {
        "places": result_places,
        "pages": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items
        }
    }