# api/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# ----- แอปหลัก -----
app = FastAPI()

# CORS (กำหนดตามต้องการ)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ----- เส้นทาง root ของ /api -----
@app.get("/")
def root():
    return {"ok": True, "service": "oONOTTY0o99-Alert API", "routes": ["/api/scan", "/api/scan/health"]}

# ----- เส้นทางของ /api/scan -----
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

# ----- include router ของ /api/scan/health -----
from api.scan.health import router as scan_health_router   # สำคัญ: path นี้ต้องตรงกับโครงสร้างโฟลเดอร์จริง
app.include_router(scan_health_router, prefix="/scan")
