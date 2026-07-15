from datetime import datetime, UTC
from typing import Optional, List
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column, Mapped

# ==== SQLAlchemy 스키마 정의 ====

class Base(DeclarativeBase):
    pass

class ContentType(Base):
    __tablename__ = "content_type"

    contentTypeId: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship to POI Items
    poi_items: Mapped[List["POIItem"]] = relationship("POIItem", back_populates="content_type")
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="categories")


class POIItem(Base):
    __tablename__ = "poi_items"

    contentid: Mapped[str] = mapped_column(String, primary_key=True)
    contenttypeid: Mapped[str] = mapped_column(String, ForeignKey("content_type.contentTypeId"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    addr1: Mapped[Optional[str]]
    addr2: Mapped[Optional[str]]
    zipcode: Mapped[Optional[str]]
    tel: Mapped[Optional[str]]
    mapx: Mapped[Optional[float]]
    mapy: Mapped[Optional[float]]
    mlevel: Mapped[Optional[str]]
    areacode: Mapped[Optional[str]]
    sigungucode: Mapped[Optional[str]]
    lDongRegnCd: Mapped[Optional[str]]
    lDongSignguCd: Mapped[Optional[str]]
    cat1: Mapped[Optional[str]]
    cat2: Mapped[Optional[str]]
    cat3: Mapped[Optional[str]]
    lclsSystm1: Mapped[Optional[str]]
    lclsSystm2: Mapped[Optional[str]]
    lclsSystm3: Mapped[Optional[str]]
    firstimage: Mapped[Optional[str]]
    firstimage2: Mapped[Optional[str]]
    cpyrhtDivCd: Mapped[Optional[str]]
    createdtime: Mapped[Optional[str]]  # Stored as text (YYYY-MM-DD HH:MM:SS)
    modifiedtime: Mapped[Optional[str]] # Stored as text (YYYY-MM-DD HH:MM:SS)

    content_type: Mapped["ContentType"] = relationship("ContentType", back_populates="poi_items")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)  # Stored as plaintext[cite: 1]
    image_path: Mapped[Optional[str]]
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Many-to-many relationship with categories
    category_id: Mapped[str] = mapped_column(String, ForeignKey("content_type.contentTypeId"), nullable=False)
    categories: Mapped[List["ContentType"]] = relationship("ContentType", back_populates="posts")
