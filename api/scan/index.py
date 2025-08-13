# api/scan/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# สำคัญ: ต้องมีตัวแปร app
app = FastAPI()

# เปิด CORS แบบกว้าง ๆ (ปรับตามต้องการ)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def scan_get():
    # ใช้สำหรับเช็กว่า endpoint /api/scan ทำงาน
    return {"ok": True, "route": "/api/scan"}

@app.post("/")
async def scan_post(req: Request):
    # รับ JSON จาก Hoppscotch/Postman เช่น {"group":"bitkub"}
    try:
        data = await req.json()
    except Exception:
        data = {}

    group = (data or {}).get("group", "default")

    # เรียก business logic (ถ้ามี)
    try:
        # อิมพอร์ตแบบ absolute จากโฟลเดอร์ api/_shared
        from api._shared.scan_logic import scan_group  # , notify_telegram (หากต้องส่งแจ้งเตือน)
        result = scan_group(group)
    except Exception as e:
        # ถ้า import/logic มีปัญหา จะไม่ให้ 500 ตกใส่ผู้ใช้
        result = {"error": str(e)}

    return {
        "ok": True,
        "input": {"group": group},
        "result": result,
    }
