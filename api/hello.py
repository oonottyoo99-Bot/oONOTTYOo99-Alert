# /api/hello.py
from fastapi import APIRouter

# ใช้ APIRouter (ไม่สร้าง app ที่นี่)
router = APIRouter()

@router.get("/")
def hello():
    return {"message": "Hello from FastAPI!"}

@router.get("/health")
def hello_health():
    # เส้นทางจริงหลัง mount จะเป็น /api/hello/health
    return {"ok": True, "route": "/api/hello/health"}
