# rebuild_api.py
from pathlib import Path
import shutil

ROOT = Path(__file__).parent.resolve()

# รายการที่จะลบทิ้งก่อน (กันของเก่าชนกัน)
TO_REMOVE = [
    ROOT / "api",
    ROOT / "app_routes",        # เคยใช้ชื่อแบบนี้ไว้ก่อนหน้า
    ROOT / "app_routes/hello",  # กันหลงเหลือ
    ROOT / "app_routes/index",  # กันหลงเหลือ
]

# เนื้อหาไฟล์ที่จะสร้าง
API_INIT = """# api/__init__.py
# ทำให้โฟลเดอร์นี้เป็น Python package
"""

API_INDEX = r'''# api/index.py
# แฟ้มนี้คือ Serverless Function ของ Vercel ที่ path /api
# ต้องมี FastAPI instance ชื่อ "app"

from fastapi import FastAPI

app = FastAPI(title="oONOTTYOo99-Alert API (minimal)")

@app.get("/")
def api_root():
    """
    GET /api
    แสดงข้อมูลแนะนำ service
    """
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": [
            "/api",
            "/api/health",
        ],
    }

@app.get("/health")
def api_health():
    """
    GET /api/health
    health check
    """
    return {"ok": True}
'''

REQUIREMENTS = """fastapi>=0.110.0
uvicorn>=0.27.0
"""

def rm(path: Path):
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

def ensure_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main():
    # 1) ลบของเก่าที่อาจชน
    for p in TO_REMOVE:
        rm(p)

    # 2) สร้างโครงสร้างใหม่แบบขั้นต่ำสุด
    ensure_text(ROOT / "api" / "__init__.py", API_INIT)
    ensure_text(ROOT / "api" / "index.py", API_INDEX)

    # 3) requirements.txt (เขียนให้ถ้าไม่มี)
    req_path = ROOT / "requirements.txt"
    if not req_path.exists() or not req_path.read_text(encoding="utf-8").strip():
        ensure_text(req_path, REQUIREMENTS)

    print("✅ Rebuilt /api for Vercel + FastAPI, files created:")
    print(" - api/__init__.py")
    print(" - api/index.py")
    print(" - requirements.txt (ensured)")

if __name__ == "__main__":
    main()
