from fastapi import FastAPI

app = FastAPI()

@app.get("/api/hello/health")
def health():
    return {"ok": True, "route": "/api/hello/health"}

