from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"ok": True, "route": "/api/hello/health"}

