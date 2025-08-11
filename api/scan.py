# api/scan.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS — ใส่โดเมนหน้าเว็บจริงของคุณ
origins = [
    "https://signal-dashboard-ui.vercel.app",  # UI ของคุณ
    "http://localhost:3000",                   # เผื่อทดสอบ local
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # ช่วงแรกถ้าติดขัด ลองเป็น ["*"] ชั่วคราวได้
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanReq(BaseModel):
    group: str

@app.post("/")
async def scan(req: ScanReq):
    # ยังไม่ต้องสแกนจริง แค่รับค่าแล้วตอบกลับเพื่อเทสให้ผ่านก่อน
    return {"ok": True, "received_group": req.group}
