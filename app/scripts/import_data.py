import os
import sys
import json
from datetime import datetime

# Adjust Python path to allow running from root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

        db_items = []
        existing_ids = {item.contentid for item in db.query(POIItem.contentid).all()}

        for item in items:
            content_id = str(item.get("contentid"))
            
            # Prevent unique key violation crash on multiple imports
            if content_id in existing_ids:
                continue

            # Parse and transform fields dynamically to fit models[cite: 1]
            poi_db_obj = POIItem(
                contentid=content_id,
                contenttypeid=str(item.get("contenttypeid")),
                title=item.get("title", "Unknown"),
                addr1=item.get("addr1"),
                addr2=item.get("addr2"),
                zipcode=item.get("zipcode"),
                tel=item.get("tel"),
                mapx=float(item.get("mapx")) if item.get("mapx") else None,
                mapy=float(item.get("mapy")) if item.get("mapy") else None,
                mlevel=item.get("mlevel"),
                areacode=item.get("areacode"),
                sigungucode=item.get("sigungucode"),
                lDongRegnCd=item.get("lDongRegnCd"),
                lDongSignguCd=item.get("lDongSignguCd"),
                cat1=item.get("cat1"),
                cat2=item.get("cat2"),
                cat3=item.get("cat3"),
                lclsSystm1=item.get("lclsSystm1"),
                lclsSystm2=item.get("lclsSystm2"),
                lclsSystm3=item.get("lclsSystm3"),
                firstimage=item.get("firstimage") or None, # convert empty string to None[cite: 1]
                firstimage2=item.get("firstimage2") or None,
                cpyrhtDivCd=item.get("cpyrhtDivCd"),
                createdtime=parse_time_format(item.get("createdtime")),
                modifiedtime=parse_time_format(item.get("modifiedtime")),
            )
            db_items.append(poi_db_obj)

        if db_items:
            db.bulk_save_objects(db_items)
            db.commit()
            print(f"Successfully imported {len(db_items)} items into the database!")
        else:
            print("No new items to import.")
    except Exception as e:
        db.rollback()
        print(f"Error during import: {e}")
    finally:
        db.close()

def import_posts(file_path: str):
    """Import posts JSON into the `posts` table.
    Supports top-level lists of post objects or a wrapper with a `posts` key.
    Each post item should include `category`, `title`, `content`, and `password`.
    """
    db = SessionLocal()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Determine if this JSON contains posts
        posts_list = []
        if isinstance(data, list):
            posts_list = data
        elif isinstance(data, dict):
            if isinstance(data.get("posts"), list):
                posts_list = data.get("posts")
            else:
                # Not a posts payload
                return

        if not posts_list:
            print("No posts found in JSON or unsupported format.")
            return

        # build a map of category name -> contentTypeId
        content_types = {ct.name: ct.contentTypeId for ct in db.query(ContentType).all()}

        existing_titles = {item.title for item in db.query(Post.title).all()}

        db_posts = []
        for item in posts_list:
            title = item.get("title")
            content = item.get("content")
            password = item.get("password")
            category_name = item.get("category")

            if not (title and content and password and category_name):
                # skip invalid entries
                continue

            category_id = content_types.get(category_name)
            if not category_id:
                print(f"Warning: category '{category_name}' not found. Skipping post '{title}'")
                continue

            # avoid duplicate by title
            if title in existing_titles:
                continue

            post_obj = Post(
                title=title,
                content=content,
                password=password,
                image_path=None,
                category_id=category_id,
            )
            db_posts.append(post_obj)

        if db_posts:
            db.bulk_save_objects(db_posts)
            db.commit()
            print(f"Successfully imported {len(db_posts)} posts from {file_path}!")
        else:
            print("No new posts to import.")

    except Exception as e:
        db.rollback()
        print(f"Error during posts import: {e}")
    finally:
        db.close()



def seed_content_types():
    db = SessionLocal()
    try:
        if db.query(ContentType).count() == 0:
            initial_types = [
                ContentType(contentTypeId="12", name="관광지"),
                ContentType(contentTypeId="14", name="문화시설"),
                ContentType(contentTypeId="15", name="축제공연행사"),
                ContentType(contentTypeId="25", name="여행코스"),
                ContentType(contentTypeId="28", name="레포츠"),
                ContentType(contentTypeId="32", name="숙박"),
                ContentType(contentTypeId="38", name="쇼핑"),
                ContentType(contentTypeId="39", name="음식점"),
            ]
            db.bulk_save_objects(initial_types)
            db.commit()
            print("---- Successfully seeded content types! ----")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding content types: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # 1. 카테고리 기초 데이터를 먼저 DB에 등록 (가장 중요)
    seed_content_types()
    
    # 2. 데이터 디렉토리 경로 설정
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' does not exist.")
        sys.exit(1)

    # 3. 폴더 내의 모든 JSON 파일을 돌며 적절하게 데이터 적재
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(data_dir, filename)
            print(f"\nProcessing file: {file_path}...")
            
            # 파일명에 'posts'가 포함되어 있거나 posts_to_import 파일인 경우
            if "posts" in filename:
                print(f"-> Detected as POSTS data. Importing to posts table...")
                import_posts(file_path)
            else:
                print(f"-> Detected as POI data. Importing to poi_items table...")
                import_json_data(file_path)

    print("\n---- JSON Data import completed! ----")