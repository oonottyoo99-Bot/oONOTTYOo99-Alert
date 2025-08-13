from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.get("/")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

@app.post("/")
async def scan_post(req: Request):
    data = {}
    try:
        data = await req.json()
    except Exception:
        pass
    return {"ok": True, "received_group": data.get("group")}
