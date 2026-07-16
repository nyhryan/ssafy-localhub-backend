from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def greeting():
    return { "msg": "Hello there!" }