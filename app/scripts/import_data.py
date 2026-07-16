import json
from datetime import datetime
from sqlalchemy import select, func, insert
from app.database import SessionLocal
from app.models import ContentType, POIItem, Post

def parse_time_format(raw_time_str: str) -> str:
    """Converts 20231015123000 to YYYY-MM-DD HH:MM:SS format safely"""
    if not raw_time_str:
        return ""
    try:
        # SQLite loves standard ISO datetime formats
        dt = datetime.strptime(raw_time_str, "%Y%m%d%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return raw_time_str  # Return raw if parsing fails

def import_json_data(file_path: str):
    db = SessionLocal()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Pull the items list out of the wrapper[cite: 1]
        items = data.get("items", [])
        if not items:
            print("No items found in JSON!")
            return
        
        existing_stmt = select(POIItem.contentid)
        existing_ids = set(db.scalars(existing_stmt).all())
        
        insert_mappings = []
        for item in items:
            content_id = str(item.get("contentid"))
            
            # Skip if this specific item is already imported
            if content_id in existing_ids:
                continue

            insert_mappings.append({
                "contentid": content_id,
                "contenttypeid": str(item.get("contenttypeid")),
                "title": item.get("title", "Unknown"),
                "addr1": item.get("addr1"),
                "addr2": item.get("addr2"),
                "zipcode": item.get("zipcode"),
                "tel": item.get("tel"),
                "mapx": float(item.get("mapx")) if item.get("mapx") else None,
                "mapy": float(item.get("mapy")) if item.get("mapy") else None,
                "mlevel": item.get("mlevel"),
                "areacode": item.get("areacode"),
                "sigungucode": item.get("sigungucode"),
                "lDongRegnCd": item.get("lDongRegnCd"),
                "lDongSignguCd": item.get("lDongSignguCd"),
                "cat1": item.get("cat1"),
                "cat2": item.get("cat2"),
                "cat3": item.get("cat3"),
                "lclsSystm1": item.get("lclsSystm1"),
                "lclsSystm2": item.get("lclsSystm2"),
                "lclsSystm3": item.get("lclsSystm3"),
                "firstimage": item.get("firstimage") or None,
                "firstimage2": item.get("firstimage2") or None,
                "cpyrhtDivCd": item.get("cpyrhtDivCd"),
                "createdtime": parse_time_format(item.get("createdtime")),
                "modifiedtime": parse_time_format(item.get("modifiedtime")),
            })

        if insert_mappings:
            # 2.0 style Bulk Insert
            db.execute(insert(POIItem), insert_mappings)
            db.commit()
            print(f"Successfully imported {len(insert_mappings)} items from {file_path}!")
        else:
            print(f"No new items to import from {file_path}.")
            
    except Exception as e:
        db.rollback()
        print(f"Error during POI import for {file_path}: {e}")
    finally:
        db.close()

def import_posts(file_path: str):
    """Import posts JSON into the `posts` table."""
    db = SessionLocal()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        posts_list = []
        if isinstance(data, list):
            posts_list = data
        elif isinstance(data, dict):
            if isinstance(data.get("posts"), list):
                posts_list = data.get("posts")
            else:
                return

        if not posts_list:
            print(f"No posts found in JSON or unsupported format: {file_path}")
            return

        # Build category map (2.0 style)
        ct_stmt = select(ContentType)
        content_types = {ct.name: ct.contentTypeId for ct in db.scalars(ct_stmt).all()}

        # Fetch existing titles to avoid duplicates (2.0 style)
        existing_titles_stmt = select(Post.title)
        existing_titles = set(db.scalars(existing_titles_stmt).all())

        insert_mappings = []
        for item in posts_list:
            title = item.get("title")
            content = item.get("content")
            password = item.get("password")
            category_name = item.get("category")

            if not (title and content and password and category_name):
                continue

            category_id = content_types.get(category_name)
            if not category_id:
                print(f"Warning: category '{category_name}' not found. Skipping post '{title}'")
                continue

            if title in existing_titles:
                continue

            insert_mappings.append({
                "title": title,
                "content": content,
                "password": password,
                "image_path": None,
                "category_id": category_id,
            })

        if insert_mappings:
            # 2.0 style Bulk Insert
            db.execute(insert(Post), insert_mappings)
            db.commit()
            print(f"Successfully imported {len(insert_mappings)} posts from {file_path}!")
        else:
            print(f"No new posts to import from {file_path}.")

    except Exception as e:
        db.rollback()
        print(f"Error during posts import for {file_path}: {e}")
    finally:
        db.close()

def seed_content_types():
    db = SessionLocal()
    try:
        # 2.0 style Count
        count_stmt = select(func.count()).select_from(ContentType)
        count = db.scalar(count_stmt)

        if count == 0:
            initial_types = [
                {"contentTypeId": "12", "name": "관광지"},
                {"contentTypeId": "14", "name": "문화시설"},
                {"contentTypeId": "15", "name": "축제공연행사"},
                {"contentTypeId": "25", "name": "여행코스"},
                {"contentTypeId": "28", "name": "레포츠"},
                {"contentTypeId": "32", "name": "숙박"},
                {"contentTypeId": "38", "name": "쇼핑"},
                {"contentTypeId": "39", "name": "음식점"},
            ]
            db.execute(insert(ContentType), initial_types)
            db.commit()
            print("---- Successfully seeded content types! ----")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding content types: {e}")
    finally:
        db.close()