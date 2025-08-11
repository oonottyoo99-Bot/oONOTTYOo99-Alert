# api/scan/index.py
from fastapi import APIRouter, Request
from api._shared.app_factory import create_app
from api._shared.scan_logic import scan_group, notify_telegram

router = APIRouter()

@router.get("/")
async def scan_get():
    return {"ok": True, "route": "/api/scan"}

@router.post("/")
async def scan_post(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    group = (data or {}).get("group", "default")

    # เรียก logic ของคุณ
    result = scan_group(group)

    # (ถ้าตั้ง TG_BOT_TOKEN / TG_CHAT_ID แล้ว) แจ้งเตือน
    try:
        text = f"[scan] group={group} items={len(result.get('items', []))}"
        notify_telegram(text)
    except Exception:
        pass

    return {"ok": True, "group": group, "result": result}

# <<< สำคัญมาก: ต้องมี app
app = create_app(router)
