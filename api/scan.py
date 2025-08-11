# api/scan.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://signal-dashboard-ui.vercel.app",
    "https://hoppscotch.io",
    "https://web.postman.co",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanReq(BaseModel):
    group: str

# ✅ ใช้ path สัมพัทธ์ต่อจาก /api/scan
@app.get("/health")
async def scan_health():
    return {"ok": True, "route": "/api/scan/health"}

@app.post("/")
async def scan(req: ScanReq):
    return {"ok": True, "received_group": req.group}
