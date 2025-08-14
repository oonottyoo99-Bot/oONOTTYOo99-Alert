# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# นำเข้า router ที่อยู่นอก api/
from app_routes.scan_router import router as scan_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# GET /api
@app.get("/")
def root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": ["/api/scan (GET, POST)", "/api/scan/health"],
    }

# รวม /api/scan/*
app.include_router(scan_router, prefix="/scan")
