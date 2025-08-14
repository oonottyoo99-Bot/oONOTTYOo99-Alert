# api/index/index.py
from fastapi import APIRouter

router = APIRouter(tags=["index"])

@router.get("/")
def index():
    return {"message": "This is index route"}
