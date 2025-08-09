# api/auto/update.py
from api._shared.app_factory import create_app

app = create_app()

@app.post("/")
def auto_update(body: dict):
    enabled = bool((body or {}).get("enabled", False))
    groups = (body or {}).get("groups", [])
    # ที่จริงควรเก็บลง DB/KV เพื่อให้ cron job มาอ่านค่าได้
    return {"ok": True, "accepted": {"enabled": enabled, "groups": groups}}

