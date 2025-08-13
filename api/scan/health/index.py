from fastapi import FastAPI

app = FastAPI()

# GET /api/scan/health
@app.get("/api/scan/health")
def health_check():
    return {"status": "ok"}
