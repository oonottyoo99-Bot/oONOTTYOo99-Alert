from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# เปิด CORS กว้าง ๆ เผื่อทดสอบ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# GET /api/scan
@app.get("/")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

# POST /api/scan
@app.post("/")
async def scan_post(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    group = data.get("group")
    return {"ok": True, "received_group": group}
