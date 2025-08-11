# api/scan/health/index.py
from fastapi import APIRouter
from api._shared.app_factory import create_app

router = APIRouter()

@router.get("/")
async def health_check():
    return {"status": "ok"}

# <<< สำคัญมาก: ต้องมี app ให้ Vercel เจอ
app = create_app(router)
