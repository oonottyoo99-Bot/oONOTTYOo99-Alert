# api/scan.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://signal-dashboard-ui.vercel.app",
    "http://localhost:3000",
    "https://hoppscotch.io",
    "https://web.postman.co",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # ถ้าทดสอบกว้างๆ ชั่วคราวใช้ ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanReq(BaseModel):
    group: str

# ✅ health ให้ใช้ path สัมพัทธ์
@app.get("/health")
async def scan_health():
    return {"ok": True, "route": "/api/scan/health"}

# ✅ endpoint หลักรับ POST ที่ root ของไฟล์ (จะกลายเป็น /api/scan)
@app.post("/")
async def scan(req: ScanReq):
    return {"ok": True, "received_group": req.group}
