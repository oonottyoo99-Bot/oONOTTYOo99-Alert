# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# รวม router จาก scan.py
from .scan import router as scan_router

app = FastAPI()

# CORS (เผื่อเรียกข้ามโดเมน)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# root: /api
@app.get("/")
def root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": ["/api/scan (GET, POST)", "/api/scan/health"],
    }

# mount: /api/scan/*
app.include_router(scan_router, prefix="/scan")
