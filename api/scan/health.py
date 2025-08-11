# api/scan/health.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")                      # สำคัญ: ใช้ "/"
def health():
    return {"ok": True, "route": "/api/scan/health"}


