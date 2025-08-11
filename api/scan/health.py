# api/scan/health.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")  # <<< สำคัญ: ต้องเป็น "/" เพราะไฟล์นี้ถูก mount ที่ /api/scan/health
def health():
    return {"ok": True, "route": "/api/scan/health"}

