#!/usr/bin/env python3
import os, shutil, textwrap, sys

ROOT = os.path.abspath(os.path.dirname(__file__))
API_DIR = os.path.join(ROOT, "api")

def write(path: str, content: str = ""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).lstrip())

def main():
    # 1) Safety check: ต้องอยู่ที่ root โปรเจกต์จริง ๆ
    must_have = ["requirements.txt", "main.py", "signals.json"]
    missing = [f for f in must_have if not os.path.exists(os.path.join(ROOT, f))]
    if missing:
        print("❌ Not at project root. Missing:", ", ".join(missing))
        sys.exit(1)

    # 2) ลบ /api เดิมทั้งหมด (ถ้ามี)
    if os.path.isdir(API_DIR):
        shutil.rmtree(API_DIR)
        print("🧹 Removed old /api directory.")

    # 3) สร้างโครงสร้างใหม่
    print("📦 Rebuilding /api for Vercel + FastAPI ...")

    # packages
    write(os.path.join(API_DIR, "__init__.py"))
    write(os.path.join(API_DIR, "routes", "__init__.py"))
    write(os.path.join(API_DIR, "routes", "index", "__init__.py"))
    write(os.path.join(API_DIR, "routes", "hello", "__init__.py"))

    # 4) สร้างไฟล์ router ย่อย (index & hello)
    write(os.path.join(API_DIR, "routes", "index", "index.py"), """
        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/")
        def index():
            return {"message": "This is index route"}
    """)

    write(os.path.join(API_DIR, "routes", "hello", "index.py"), """
        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/")
        def hello():
            return {"message": "Hello from FastAPI!"}
    """)

    # 5) สร้างไฟล์หลัก /api/index.py (ไฟล์นี้คือฟังก์ชันบน Vercel ที่แม็พกับ /api)
    write(os.path.join(API_DIR, "index.py"), """
        # /api/index.py  (Vercel -> /api)
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        # ✅ Vercel ต้องการตัวแปรระดับโมดูลชื่อ 'app'
        app = FastAPI(title="oONOTTYOo99-Alert API")

        # เปิด CORS ชั่วคราว (ให้ทดสอบได้จากทุกโดเมน)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        )

        # ---------- Root (/api) ----------
        @app.get("/")
        def api_root():
            return {
                "ok": True,
                "service": "oONOTTYOo99-Alert API",
                "routes": ["/api", "/api/health", "/api/index", "/api/hello"],
            }

        # ---------- Health (/api/health) ----------
        @app.get("/health")
        def api_health():
            return {"ok": True}

        # ---------- include sub-routers ----------
        # ใช้ absolute import เพื่อให้ Vercel/Python หาแพ็กเกจเจอแน่นอน
        from api.routes.index.index import router as index_router
        from api.routes.hello.index import router as hello_router

        app.include_router(index_router, prefix="/index")
        app.include_router(hello_router, prefix="/hello")
    """)

    print("✅ Rebuilt. Files created:")
    for p in [
        "api/__init__.py",
        "api/index.py",
        "api/routes/__init__.py",
        "api/routes/index/__init__.py",
        "api/routes/index/index.py",
        "api/routes/hello/__init__.py",
        "api/routes/hello/index.py",
    ]:
        print(" -", p)

    print("\nNext:")
    print("  1) Commit & push โค้ดขึ้น GitHub ให้ Vercel deploy อัตโนมัติ")
    print("     git add -A && git commit -m \"Rebuild /api skeleton\" && git push")
    print("  2) เปิดทดสอบ:")
    print("     • /api           -> https://<your-app>.vercel.app/api")
    print("     • /api/health    -> https://<your-app>.vercel.app/api/health")
    print("     • /api/index     -> https://<your-app>.vercel.app/api/index")
    print("     • /api/hello     -> https://<your-app>.vercel.app/api/hello")

if __name__ == "__main__":
    main()
