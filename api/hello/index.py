# api/hello/index.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def hello_home():
    return {"message": "Hello from FastAPI!"}

