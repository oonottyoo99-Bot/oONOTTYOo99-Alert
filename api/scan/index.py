# api/scan/index.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ใช้ logic ที่คุณมีอยู่แล้ว
from api._shared.scan_logic import scan_group, notify_telegram

app = FastAPI()

# CORS (ถ้าจะล็อกโดเมน ค่อยใส่ลิสต์แทน "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GET แบบเช็คเส้นทางเฉย ๆ
@app.get("/")
def scan_get():
    return {"ok": True, "route": "/api/scan"}

# POST เรียกสแกนจริง
@app.post("/")
async def scan_post(req: Request):
    try:
        data = await req.json()
    except Exception:
        raise HTTPException(400, "invalid json")

    group = (data or {}).get("group")
    if not group:
        raise HTTPException(400, "missing 'group'")

    # เรียก logic จริง
    result = scan_group(group)

    # แจ้งเตือน Telegram (ถ้าตั้ง env แล้ว)
    notified = False
    try:
        items = result.get("items", [])
        if items is not None:
            lines = [f"{i.get('symbol','?')}: {i.get('signal','-')}" for i in items]
            text = f"[{group}] {len(items) if isinstance(items, list) else 0} signals\n" + "\n".join(lines)
            notify_telegram(text)
            notified = True
    except Exception:
        notified = False

    return {"ok": True, "group": group, "result": result, "notified": notified}
