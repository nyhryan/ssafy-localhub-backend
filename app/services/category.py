from math import ceil

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import ContentType, POIItem


def get_category_places(
    db: Session,
    filter: str | None = None,
    page: int = 1,
    items_per_page: int = 10,
):
    stmt = select(POIItem)

    if filter:
        category = db.scalars(
            select(ContentType).where(ContentType.name == filter)
        ).first()

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 카테고리가 존재하지 않습니다.",
            )

        stmt = stmt.where(POIItem.contenttypeid == category.contentTypeId)

    total_items = db.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one() or 0
    total_pages = ceil(total_items / items_per_page) if total_items > 0 else 0

    db_places = db.scalars(
        stmt.offset((page - 1) * items_per_page).limit(items_per_page)
    ).all()

    places = [
        {
            "id": place.contentid,
            "title": place.title,
            "address": place.addr1,
            "image": place.firstimage2,
            "mapx": place.mapx,
            "mapy": place.mapy,
            "category_name": place.content_type.name if place.content_type else None,
        }
        for place in db_places
    ]

    return {
        "places": places,
        "pages": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
        },
    }