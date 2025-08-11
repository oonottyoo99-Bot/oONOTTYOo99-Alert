# api/scan.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# อนุญาตต้นทางที่ต้องเรียกเข้ามา (เพิ่ม hoppscotch/postman web ไว้สำหรับทดสอบด้วย)
origins = [
    "https://signal-dashboard-ui.vercel.app",
    "http://localhost:3000",
    "https://hoppscotch.io",
    "https://web.postman.co",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # ถ้าจะทดสอบให้ผ่านหมดชั่วคราว: ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanReq(BaseModel):
    group: str

# health check ง่ายๆ
@app.get("/api/scan/health")
async def scan_health():
    return {"ok": True, "route": "/api/scan/health"}

# endpoint หลัก (ต้องเป็น POST)
@app.post("/api/scan")
async def scan(req: ScanReq):
    # ตรงนี้ยังคืนค่าเฉยๆ ก่อน ไว้ค่อยเชื่อม logic สแกนจริง
    return {"ok": True, "received_group": req.group}
