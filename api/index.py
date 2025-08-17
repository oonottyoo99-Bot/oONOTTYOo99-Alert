from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="oONOTTYOo99-Alert API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
def api_root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": ["/api", "/api/health", "/api/index", "/api/hello"],
    }

@app.get("/health")
def api_health():
    return {"ok": True}

# รวม sub-routers ถ้ามี (ไม่มีก็ผ่านได้)
try:
    from api._routes.index import router as index_router
    app.include_router(index_router, prefix="/index")
except Exception:
    pass

try:
    from api._routes.hello import router as hello_router
    app.include_router(hello_router, prefix="/hello")
except Exception:
    pass
