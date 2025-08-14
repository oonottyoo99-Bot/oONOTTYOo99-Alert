# api/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from time import time

app = FastAPI(title="oONOTTYOo99-Alert API")

# CORS (เปิดกว้างไว้ก่อน)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# ---------- Root /api ----------
@app.get("/")
def api_root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": [
            "/api",
            "/api/hello",
            "/api/ping",
            "/api/results",
            "/api/scan",
            "/api/scan/health",
        ],
    }


# ---------- Hello ----------
@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI!"}


# ---------- Ping ----------
@app.get("/ping")
def ping():
    return {"pong": True, "ts": int(time())}


# ---------- Results (stub) ----------
@app.get("/results")
def results(id: str | None = None):
    return {
        "ok": True,
        "note": "No persistent storage connected yet. Use /api/scan response for now.",
        "id": id,
        "data": None,
    }


# ---------- Scan (mock) ----------
@app.get("/scan")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

@app.post("/scan")
async def scan_post(req: Request):
    # รับ body เป็น JSON: {"group": "xxx"}
    try:
        data = await req.json()
    except Exception:
        data = {}
    group = data.get("group")
    # ตอบ mock กลับไปให้ทดสอบการไหลของงาน
    return {
        "ok": True,
        "received_group": group,
        "items": [
            {"symbol": "AAPL", "signal": "BUY"},
            {"symbol": "MSFT", "signal": "HOLD"},
        ],
        "ts": int(time()),
    }

@app.get("/scan/health")
def scan_health():
    return {"ok": True, "route": "/api/scan/health"}
