# api/scan.py
from fastapi import BackgroundTasks
from api._shared.app_factory import create_app
from api._shared.scan_logic import scan_group, notify_telegram

app = create_app()

@app.post("/")
def scan(body: dict, bg: BackgroundTasks):
    group = (body or {}).get("group")
    if not group:
        return {"ok": False, "error": "group is required"}

    # เรียกลอจิกจริง (ตอนนี้เป็น mock)
    result = scan_group(group)

    # แจ้งเตือน Telegram (ทำใน background)
    bg.add_task(
        notify_telegram,
        f"[SCAN DONE] {group} → {len(result['items'])} result(s)"
    )

    # ส่งผลกลับหน้าเว็บ
    return {"ok": True, "data": result}

