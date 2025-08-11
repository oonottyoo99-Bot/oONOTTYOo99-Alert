from fastapi import FastAPI

app = FastAPI()

@app.get("/api/index")
def index():
    return {"message": "This is index route"}

@app.get("/api/index/health")
def index_health():
    return {"ok": True, "route": "/api/index"}
