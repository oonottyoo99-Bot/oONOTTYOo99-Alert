# api/scan.py
from fastapi import APIRouter, Request

router = APIRouter()

# GET /api/scan
@router.get("/")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

# POST /api/scan
@router.post("/")
async def scan_post(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    group = data.get("group")
    # ตรงนี้ค่อยไปเชื่อม logic จริงภายหลังได้
    return {"ok": True, "received_group": group}

# GET /api/scan/health
@router.get("/health")
def scan_health():
    return {"ok": True, "route": "/api/scan/health"}

