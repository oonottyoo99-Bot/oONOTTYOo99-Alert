# api/results.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def results(id: str | None = None):
    return {
        "ok": True,
        "note": "Simple stub. Replace with real logic later.",
        "id": id,
        "data": None
    }
