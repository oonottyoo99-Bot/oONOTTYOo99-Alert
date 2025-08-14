# api/scan/health.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health_check():
    return {"ok": True, "route": "/api/scan/health"}

