# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# นำเข้า routers ย่อย (ถ้ามี)
try:
    from api._routes.index.index import router as index_router
    from api._routes.hello.index import router as hello_router
except Exception:
    index_router = None
    hello_router = None

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

# รวม routers ย่อย (มีไฟล์คงเดิมอยู่แล้ว)
if index_router:
    app.include_router(index_router, prefix="/index")
if hello_router:
    app.include_router(hello_router, prefix="/hello")
