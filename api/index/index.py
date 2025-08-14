# /api/index/index.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def index():
    return {"message": "This is index route"}
