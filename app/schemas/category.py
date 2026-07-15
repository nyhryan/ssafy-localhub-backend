from typing import List, Optional
from pydantic import BaseModel


class PlaceSchema(BaseModel):
    id: str
    title: str
    address: Optional[str] = None
    image: Optional[str] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None
    category_name: Optional[str] = None

    class Config:
        from_attributes = True

class PageInfoSchema(BaseModel):
    current_page: int
    total_pages: int
    total_items: int

class CategoryResponseSchema(BaseModel):
    places: List[PlaceSchema]
    pages: PageInfoSchema