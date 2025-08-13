# api/scan/health/index.py
from fastapi import FastAPI

app = FastAPI()

# GET /api/scan/health -> health check
@app.get("/")
def health_check():
    return {"status": "ok"}
