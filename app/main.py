from fastapi import FastAPI
from .database import Base, engine
from . import models
from .api.v1 import greeting

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(greeting.router, prefix="/api/v1")