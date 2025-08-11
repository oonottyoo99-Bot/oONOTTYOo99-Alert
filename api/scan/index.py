from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# อนุญาต CORS ให้ UI คุณเรียกได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://signal-dashboard-ui.vercel.app",
        "http://localhost:3000",
        "*"  # ชั่วคราวช่วงทดสอบ จะคุมให้แคบลงภายหลังได้
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GET ไว้ทดสอบด้วยเบราว์เซอร์
@app.get("/")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

# POST สำหรับยิงจริงจาก UI / Hoppscotch / Postman
@app.post("/")
async def scan_post(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    group = data.get("group")
    return {"ok": True, "received_group": group}

