# api/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (เปิดกว้างสำหรับทดสอบ)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ---- root: /api ----
@app.get("/")
def root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": ["/api/scan", "/api/scan/health"]
    }

# ---- /api/scan ----
@app.get("/scan")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

@app.post("/scan")
async def scan_post(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    group = data.get("group")
    return {"ok": True, "received_group": group}

# ---- include router: /api/scan/health ----
from api._shared.scan_health import router as scan_health_router
app.include_router(scan_health_router, prefix="/scan")
