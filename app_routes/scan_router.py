from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

@router.post("/")
async def scan_post(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    return {"ok": True, "received_group": data.get("group")}

@router.get("/health")
def scan_health():
    return {"ok": True, "route": "/api/scan/health"}

