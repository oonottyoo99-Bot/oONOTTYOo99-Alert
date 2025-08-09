from fastapi import FastAPI

app = FastAPI()

@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI!"}

@app.get("/api/hello/health")
def hello_health():
    return {"ok": True, "route": "/api/hello"}
