from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ปลด CORS สำหรับทดสอบ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")                 # << เส้นทาง /api/scan (GET)
def root():
    return {"ok": True, "route": "/api/scan"}

@app.post("/")                # << เส้นทาง /api/scan (POST)
async def scan(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    return {"ok": True, "received_group": data.get("group")}
