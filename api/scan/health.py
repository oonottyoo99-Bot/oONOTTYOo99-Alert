# api/scan/health.py
from fastapi import APIRouter

# สำคัญ: ต้องชื่อ router
router = APIRouter()

@router.get("/health", summary="Health check for scan service")
async def health_check():
    # ส่งโครงสร้างที่เช็คง่าย ๆ
    return {"ok": True, "route": "/api/scan/health"}
