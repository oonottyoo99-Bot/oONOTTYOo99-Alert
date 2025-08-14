# api/scan/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# เปิด CORS ให้ทดสอบจากเบราว์เซอร์/Hoppscotch ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
def scan_get():
    # GET สำหรับเช็คง่ายๆ ว่าตัว /api/scan ทำงานแล้ว
    return {"ok": True, "route": "/api/scan"}

@app.post("/")
async def scan_post(req: Request):
    # รับ JSON เช่น {"group":"bitkub"}
    try:
        data = await req.json()
    except Exception:
        data = {}
    group = data.get("group")
    # ตรงนี้ค่อยไปต่อยอดเรียก logic จริงในอนาคต
    return {"ok": True, "received_group": group}

