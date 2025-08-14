# api/hello/index.py
from fastapi import APIRouter

router = APIRouter(tags=["hello"])

@router.get("/")
def hello():
    return {"message": "Hello from FastAPI!"}
