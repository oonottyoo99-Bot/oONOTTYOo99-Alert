# api/scan/health.py
from fastapi import FastAPI

app = FastAPI()

# GET /api/scan/health
@app.get("/")
def health_check():
    return {"status": "ok"}

