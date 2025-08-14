from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": ["/api/scan", "/api/scan/health"],
    }
