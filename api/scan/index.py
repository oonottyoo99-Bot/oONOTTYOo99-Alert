# api/scan/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS ให้เรียกจากที่ไหนก็ได้ (จะคุมเข้มภายหลังก็ได้)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# GET /api/scan -> ใช้เช็คว่า route ติดหรือยัง
@app.get("/")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

# POST /api/scan -> ยิงสแกน
@app.post("/")
async def scan_post(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    group = data.get("group")
    return {"ok": True, "received_group": group}
