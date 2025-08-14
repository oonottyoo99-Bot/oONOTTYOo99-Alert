# api/index.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "ok": True,
        "service": "oONOTTYoo99-Alert API",
        "routes": ["/api/scan", "/api/scan/health"]
    }
