from fastapi import FastAPI

app = FastAPI()

@app.get("/api/index/health")
def health():
    return {"ok": True, "route": "/api/index/health"}

