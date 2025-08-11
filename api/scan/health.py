# api/scan/health.py
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def health():
    return {"ok": True, "route": "/api/scan/health"}

# ✅ DEBUG: จับทุกเส้นทาง
@app.api_route("/{p:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def health_catch_all(p: str, request: Request):
    return {
        "debug": "health catch-all",
        "path_in_app": f"/{p}",
        "url_seen_by_app": request.url.path,
    }
