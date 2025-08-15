# api/index/index.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def index_home():
    return {"message": "This is index route"}
