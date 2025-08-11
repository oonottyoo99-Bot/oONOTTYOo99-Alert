# api/scan/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# เปิด CORS กว้างๆ สำหรับทดสอบ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

@app.post("/")
async def scan_post(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}

    group = data.get("group")
    # จะทำ logic จริงทีหลังค่อยต่อเพิ่ม
    return {"ok": True, "received_group": group}
