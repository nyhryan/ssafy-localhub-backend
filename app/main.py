from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.scripts.import_data import import_json_data, import_posts, seed_content_types
from .database import Base, engine
from .api.v1 import category, posts

Base.metadata.create_all(bind=engine)

def populate_database() -> None:
    seed_content_types()

    data_dir = Path(__file__).resolve().parent.parent / "data"
    if not data_dir.exists():
        print(f"Error: Data directory '{data_dir}' does not exist.")
        return

    for file_path in data_dir.glob("*.json"):
        print(f"\nProcessing file: {file_path}...")

        if "posts" in file_path.name:
            print("-> Detected as POSTS data. Importing to posts table...")
            import_posts(str(file_path))
        else:
            print("-> Detected as POI data. Importing to poi_items table...")
            import_json_data(str(file_path))

    print("\n---- JSON Data import completed! ----")

@asynccontextmanager
async def lifespan(app: FastAPI):
    populate_database()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "https://frolicking-valkyrie-bfd943.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router, prefix="/api/v1")
app.include_router(category.router, prefix="/api/v1")
