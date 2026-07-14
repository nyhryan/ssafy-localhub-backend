from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def greeting():
    return { "msg": "Hello there!" }