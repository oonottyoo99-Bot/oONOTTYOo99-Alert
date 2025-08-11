# api/scan.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# อนุญาตให้หน้า UI ของคุณเรียกได้
origins = [
    "https://signal-dashboard-ui.vercel.app",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # ถ้ายังติด ให้ลอง ["*"] ชั่วคราวได้
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanReq(BaseModel):
    group: str

@app.post("/")
async def scan(req: ScanReq):
    # ตอนนี้ให้ตอบกลับเฉย ๆ เพื่อเทส
    return {"ok": True, "received_group": req.group}
