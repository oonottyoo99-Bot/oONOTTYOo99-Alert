# rebuild_api.py
# ใช้สร้างโครงสร้าง /api สำหรับ Vercel + FastAPI แบบถูกต้อง และล้างไฟล์กวนใจอัตโนมัติ

import os, shutil, textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.join(ROOT, "api")

# โครงสร้าง/ไฟล์ที่ต้องการคงไว้สุดท้าย
KEEP = {
    "api": {
        "__init__.py": "",
        "index.py": "MAIN",          # ไฟล์ serverless function หลัก (มี app = FastAPI)
        "_routes": {                 # เก็บ sub-routers (ไม่ใช่ฟังก์ชันแยก)
            "__init__.py": "",
            "index": {
                "__init__.py": "",
                "index.py": "ROUTER_INDEX"
            },
            "hello": {
                "__init__.py": "",
                "index.py": "ROUTER_HELLO"
            }
        }
    }
}

MAIN_INDEX_PY = """\
# api/index.py (MAIN APP)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ⚠️ สำคัญ: import แบบ absolute จากแพ็กเกจภายใต้ api/_routes/*
from api._routes.index.index import router as index_router
from api._routes.hello.index import router as hello_router

app = FastAPI(title="oONOTTYOo99-Alert API")

# เปิด CORS กว้าง ๆ (เพื่อทดสอบ)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ---------- Root /api ----------
@app.get("/")
def api_root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": ["/api", "/api/health", "/api/index", "/api/hello"],
    }

# ---------- Health /api/health ----------
@app.get("/health")
def api_health():
    return {"ok": True}

# ---------- include sub-routers ----------
app.include_router(index_router, prefix="/index")
app.include_router(hello_router, prefix="/hello")
"""

ROUTER_INDEX = """\
# api/_routes/index/index.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def index():
    return {"message": "This is index route"}
"""

ROUTER_HELLO = """\
# api/_routes/hello/index.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def hello():
    return {"message": "Hello from FastAPI!"}
"""

def write_file(path: str, content: str = ""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def ensure_clean_api():
    # ลบทุกอย่างใต้ api/ ออกก่อน (ถ้ามี) เพื่อกันชนกับ serverless อื่น ๆ
    if os.path.isdir(API_DIR):
        shutil.rmtree(API_DIR)
    os.makedirs(API_DIR, exist_ok=True)

def materialize(tree: dict, base: str):
    for name, val in tree.items():
        path = os.path.join(base, name)
        if isinstance(val, dict):
            os.makedirs(path, exist_ok=True)
            materialize(val, path)
        else:
            # เลือกคอนเทนต์ตามชนิดไฟล์พิเศษ
            if val == "MAIN":
                content = MAIN_INDEX_PY
            elif val == "ROUTER_INDEX":
                content = ROUTER_INDEX
            elif val == "ROUTER_HELLO":
                content = ROUTER_HELLO
            else:
                content = ""
            write_file(path, textwrap.dedent(content))

def ensure_requirements():
    req_path = os.path.join(ROOT, "requirements.txt")
    if not os.path.exists(req_path):
        write_file(
            req_path,
            textwrap.dedent("""\
            fastapi>=0.110.0
            uvicorn[standard]>=0.27.0
            """),
        )

def main():
    ensure_clean_api()
    materialize(KEEP, ROOT)
    ensure_requirements()

    print("✅ Rebuilt /api for Vercel + FastAPI, files created:")
    for root, dirs, files in os.walk(API_DIR):
        for f in files:
            print(" -", os.path.relpath(os.path.join(root, f), ROOT))

if __name__ == "__main__":
    main()

