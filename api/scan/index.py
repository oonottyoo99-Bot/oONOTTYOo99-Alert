# api/scan/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# เส้นทางหลักของ /api/scan
@app.get("/")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

@app.post("/")
async def scan_post(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    return {"ok": True, "received_group": data.get("group")}

# ✅ DEBUG: จับทุกเส้นทางเพื่อดูว่า FastAPI เห็น path อะไร
@app.api_route("/{p:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def scan_catch_all(p: str, request: Request):
    return {
        "debug": "scan catch-all",
        "path_in_app": f"/{p}",
        "url_seen_by_app": request.url.path,
    }
