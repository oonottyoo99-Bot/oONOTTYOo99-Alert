# api/scan.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ค่อยมากำหนดแคบลงทีหลัง
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")                     # สำคัญ: ใช้ "/" เพราะ Vercel mount ที่ /api/scan ให้แล้ว
async def scan(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    group = data.get("group")
    return {"ok": True, "received_group": group}
