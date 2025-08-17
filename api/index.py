# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="oONOTTYOo99-Alert API")

# CORS (เปิดกว้างตามที่คุณใช้)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# -------- Root /api --------
@app.get("/")
def api_root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": ["/api", "/api/health", "/api/index", "/api/hello"],
    }

# -------- Health /api/health --------
@app.get("/health")
def api_health():
    return {"ok": True}

# -------- รวม sub-routers ถ้ามี (ไม่บังคับ) --------
try:
    from api._routes.index import router as index_router  # ถ้ามีโครงสร้างแบบ api/_routes/index.py
    app.include_router(index_router, prefix="/index")
except Exception:
    pass

try:
    from api._routes.hello import router as hello_router  # ถ้ามีโครงสร้างแบบ api/_routes/hello.py
    app.include_router(hello_router, prefix="/hello")
except Exception:
    pass
