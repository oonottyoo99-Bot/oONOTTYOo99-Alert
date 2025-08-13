# api/scan/health/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# สำคัญ: ต้องมีตัวแปร app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    # ใช้สำหรับเช็กสุขภาพฟังก์ชัน /api/scan/health
    return {"ok": True, "route": "/api/scan/health"}
