# app/api/v1/category.py (에러 예외 처리 반영 버전)
from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db  
from app.models import POIItem, ContentType 

router = APIRouter()

# --- (Pydantic Schema 부분은 동일하게 유지) ---
class PlaceSchema(BaseModel):
    id: str
    title: str
    address: Optional[str] = None
    image: Optional[str] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None

    class Config:
        from_attributes = True

class PageInfoSchema(BaseModel):
    current_page: int
    total_pages: int
    total_items: int

class CategoryResponseSchema(BaseModel):
    places: List[PlaceSchema]
    pages: PageInfoSchema


# --- API 엔드포인트 구현 (500 에러 예외 처리 추가) ---
@router.get("/categories", response_model=CategoryResponseSchema)
def get_category_places(
    filter: Optional[str] = Query(None, description="카테고리 필터 (contentTypeId 값 입력)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    db: Session = Depends(get_db)
):
    try:
        # 1. POIItem 테이블 조회 쿼리 빌더 생성
        query = db.query(POIItem)
        
        # 2. 카테고리 필터링 적용
        if filter:
            query = query.filter(POIItem.contenttypeid == filter)
            
        # 3. 페이지네이션 계산
        items_per_page = 10
        total_items = query.count()
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # 데이터 슬라이싱
        offset = (page - 1) * items_per_page
        db_places = query.offset(offset).limit(items_per_page).all()
        
        # 4. 데이터 매칭 가공
        result_places = []
        for place in db_places:
            result_places.append({
                "id": place.contentid,
                "title": place.title,
                "address": place.addr1,
                "image": place.firstimage2,
                "mapx": place.mapx,
                "mapy": place.mapy
            })
            
        # 5. 정상 처리 응답 (200 OK)
        return {
            "places": result_places,
            "pages": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items
            }
        }

    except Exception as e:
        # DB 에러 등 예상치 못한 오류가 발생하면 500 Internal Server Error를 직접 발생시킴
        # 백엔드 콘솔에 에러 로그를 기록함
        print(f"[Error] /api/v1/categories 호출 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
        )