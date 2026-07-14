from fastapi import FastAPI

from .api.v1 import greeting

app = FastAPI()
app.include_router(greeting.router, prefix="/api/v1")