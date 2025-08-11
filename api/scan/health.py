from fastapi import FastAPI

app = FastAPI()

@app.get("/")                 # << เส้นทาง /api/scan/health (GET)
def health():
    return {"ok": True, "route": "/api/scan/health"}
