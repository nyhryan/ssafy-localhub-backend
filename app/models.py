from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from .database import Base

# ==== SQLAlchemy 스키마 정의 ====

class ContentType(Base):
    __tablename__ = "content_type"

    contentTypeId = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)

    # Relationship to POI Items
    poi_items = relationship("POIItem", back_populates="content_type")
    posts = relationship("Post", back_populates="categories")


class POIItem(Base):
    __tablename__ = "poi_items"

    contentid = Column(String, primary_key=True)
    contenttypeid = Column(String, ForeignKey("content_type.contentTypeId"), nullable=False)
    title = Column(String, nullable=False)
    addr1 = Column(String, nullable=True)
    addr2 = Column(String, nullable=True)
    zipcode = Column(String, nullable=True)
    tel = Column(String, nullable=True)
    mapx = Column(Float, nullable=True)
    mapy = Column(Float, nullable=True)
    mlevel = Column(String, nullable=True)
    areacode = Column(String, nullable=True)
    sigungucode = Column(String, nullable=True)
    lDongRegnCd = Column(String, nullable=True)
    lDongSignguCd = Column(String, nullable=True)
    cat1 = Column(String, nullable=True)
    cat2 = Column(String, nullable=True)
    cat3 = Column(String, nullable=True)
    lclsSystm1 = Column(String, nullable=True)
    lclsSystm2 = Column(String, nullable=True)
    lclsSystm3 = Column(String, nullable=True)
    firstimage = Column(String, nullable=True)
    firstimage2 = Column(String, nullable=True)
    cpyrhtDivCd = Column(String, nullable=True)
    createdtime = Column(String, nullable=True)  # Stored as text (YYYY-MM-DD HH:MM:SS)
    modifiedtime = Column(String, nullable=True) # Stored as text (YYYY-MM-DD HH:MM:SS)

    content_type = relationship("ContentType", back_populates="poi_items")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    password = Column(String, nullable=False)  # Stored as plaintext[cite: 1]
    image_path = Column(String, nullable=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Many-to-many relationship with categories
    category_id = Column(String, ForeignKey("content_type.contentTypeId"), nullable=False)
    categories = relationship("ContentType", back_populates="posts")
