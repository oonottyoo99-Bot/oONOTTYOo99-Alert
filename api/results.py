# api/results.py
from api._shared.app_factory import create_app

app = create_app()

@app.get("/")
def results(id: str | None = None):
    """
    Stub (ยังไม่เชื่อม storage)
    - ถ้าในอนาคตใช้ DB/Redis → อ่านผลล่าสุดหรืออ่านตาม id ได้ที่นี่
    """
    return {
        "ok": True,
        "note": "No persistent storage connected yet. Use /api/scan response for now.",
        "data": None
    }

