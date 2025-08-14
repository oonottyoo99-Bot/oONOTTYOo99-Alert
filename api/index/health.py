# api/index/health.py
from fastapi import APIRouter

router = APIRouter(tags=["index-health"])

@router.get("/health")
def index_health():
    return {
        "ok": True,
        "route": "/api/index/health"
    }
