# api/scan.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# อนุญาตโดเมนที่เรียกใช้ API (เพิ่ม/ลบได้)
ALLOWED_ORIGINS = [
    "https://signal-dashboard-ui.vercel.app",
    "http://localhost:3000",
    "https://hoppscotch.io",
    "https://web.postman.co",
    "https://www.postman.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Models -----
class ScanReq(BaseModel):
    group: str


# ----- Routes -----
# GET /api/scan  → สำหรับเปิดในเบราว์เซอร์
@app.get("/")
async def scan_get():
    return {
        "status": "ok",
        "route": "/api/scan",
        "methods": ["GET", "POST"],
        "how_to_use": {
            "POST": {"body": {"group": "bitkub"}},
            "health": "/api/scan/health",
        },
    }

# GET /api/scan/health  → health check
@app.get("/health")
async def scan_health():
    return {"ok": True, "route": "/api/scan/health"}

# POST /api/scan  → เรียกใช้งานจริง (ยิงจากเว็บ/เครื่องมือทดสอบ)
@app.post("/")
async def scan_post(req: ScanReq):
    group = req.group.strip().lower()
    # TODO: ใส่ลอจิกสแกนจริงของคุณตรงนี้
    return {"ok": True, "received_group": group}
