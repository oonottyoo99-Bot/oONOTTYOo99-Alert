# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="oONOTTYOo99-Alert API")

# CORS กว้างๆ (ช่วงทดสอบ)
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

# -------- include sub-routers (ใช้ relative import) --------
# ⚠️ สำคัญ: ใช้จุดนำหน้า .index .hello เพื่ออิงโฟลเดอร์เดียวกันกับไฟล์นี้
try:
    from .index.index import router as index_router
    from .hello.index import router as hello_router

    app.include_router(index_router, prefix="/index")
    app.include_router(hello_router, prefix="/hello")
except Exception as e:
    # ทางหนีไฟ: ถ้า import พลาด จะมี endpoint ให้เช็คสาเหตุได้ที่ /api/debug_import
    @app.get("/debug_import")
    def debug_import():
        return {"import_error": str(e)}
