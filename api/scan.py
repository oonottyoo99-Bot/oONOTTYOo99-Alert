# api/scan.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS — ชั่วคราวเปิดกว้างไว้ก่อน
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ใส่โดเมนจริงทีหลัง เช่น https://signal-dashboard-ui.vercel.app
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")  # <<< สำคัญ: ต้องเป็น "/" เพราะไฟล์นี้ถูก mount ที่ /api/scan
async def scan(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    group = data.get("group")
    return {"ok": True, "received_group": group}
