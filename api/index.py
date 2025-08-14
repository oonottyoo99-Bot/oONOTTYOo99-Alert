# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ⬇️ นำเข้า router จากโมดูลย่อยที่แปลงเป็น APIRouter แล้ว
from api.index.index import router as index_router       # ให้บริการ /api/index/*
from api.hello.index import router as hello_router       # ให้บริการ /api/hello/*

app = FastAPI(title="oONOTTYOo99-Alert API")

# CORS (อนุญาตทุก origin ไว้ก่อนสำหรับทดสอบ)
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
            "/api/health",
            "/api/index",
            "/api/hello",
        ],
    }

# ---------- Health /api/health ----------
@app.get("/health")
def api_health():
    return {"ok": True}

# ---------- รวม router ย่อย ----------
app.include_router(index_router, prefix="/index")
app.include_router(hello_router, prefix="/hello")
