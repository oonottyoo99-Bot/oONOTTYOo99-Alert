# api/hello/health.py
from fastapi import APIRouter

router = APIRouter(tags=["hello-health"])

@router.get("/health")
def hello_health():
    return {
        "ok": True,
        "route": "/api/hello/health"
    }
