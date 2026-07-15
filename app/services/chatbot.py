from sqlalchemy.orm import Session

from app.models import ContentType, POIItem, Post

# 1. Define Python functions that actually query your database
def search_local_pois(db: Session, category_name: str = None, query_location: str = None):
    """Query local SQLite database for POIs matching category and location"""
    stmt = db.query(POIItem)
    
    if category_name:
        # Join to find the right ContentType ID
        stmt = stmt.join(ContentType).filter(ContentType.name.ilike(f"%{category_name}%"))
    if query_location:
        stmt = stmt.filter(POIItem.addr1.ilike(f"%{query_location}%"))
        
    results = stmt.limit(5).all()
    return [
        {
            "title": r.title,
            "address": r.addr1,
            "tel": r.tel,
            "mapx": r.mapx,
            "mapy": r.mapy
        } for r in results
    ]

def get_community_reviews(db: Session, category_name: str):
    """Retrieve community posts/reviews written by users in a category"""
    results = db.query(Post).join(ContentType).filter(
        ContentType.name.ilike(f"%{category_name}%")
    ).order_by(Post.likes.desc()).limit(3).all()
    
    return [
        {
            "title": r.title,
            "content": r.content,
            "likes": r.likes,
            "views": r.views
        } for r in results
    ]