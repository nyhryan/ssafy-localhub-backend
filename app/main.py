from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from . import models
from .api.v1 import greeting, category, posts

Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(greeting.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
app.include_router(category.router, prefix="/api/v1")
