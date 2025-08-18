# rebuild_api_min.py
# ลบ api เก่า → สร้างโครงใหม่ + ใส่โค้ดครบ (2–7) + vercel.json + requirements.txt

import os, shutil, textwrap, subprocess, sys

ROOT = os.getcwd()

def write(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).lstrip())

def main():
    # 0) ลบโฟลเดอร์ api เก่าทิ้ง (ถ้ามี)
    api_dir = os.path.join(ROOT, "api")
    if os.path.isdir(api_dir):
        shutil.rmtree(api_dir)

    # 1) requirements.txt (เบาและพอ)
    write(
        os.path.join(ROOT, "requirements.txt"),
        """
        fastapi==0.110.0
        uvicorn==0.27.0
        """,
    )

    # 2) vercel.json (runtime ถูกต้อง + route /api → api/index.py)
    write(
        os.path.join(ROOT, "vercel.json"),
        r"""
        {
          "functions": {
            "api/**/*.py": {
              "runtime": "python3.11"
            }
          },
          "routes": [
            { "src": "^/api$", "dest": "api/index.py" }
          ]
        }
        """,
    )

    # 3) api/index.py (มี app + /api + /api/health และ include routers)
    write(
        os.path.join(ROOT, "api/index.py"),
        """
        from fastapi import FastAPI
        from api._routes.index.index import router as index_router
        from api._routes.hello.index import router as hello_router

        app = FastAPI(title="oONOTTYOo99-Alert API")

        @app.get("/")
        def api_root():
            return {
                "ok": True,
                "service": "oONOTTYOo99-Alert API",
                "routes": ["/api", "/api/health", "/api/index", "/api/hello"],
            }

        @app.get("/health")
        def api_health():
            return {"ok": True}

        app.include_router(index_router, prefix="/index")
        app.include_router(hello_router, prefix="/hello")
        """,
    )

    # 4) api/_routes/index/__init__.py
    write(os.path.join(ROOT, "api/_routes/index/__init__.py"), "# package\n")

    # 5) api/_routes/index/index.py
    write(
        os.path.join(ROOT, "api/_routes/index/index.py"),
        """
        from fastapi import APIRouter
        router = APIRouter()

        @router.get("/")
        def read_index():
            return {"message": "This is index route"}
        """,
    )

    # 6) api/_routes/hello/__init__.py
    write(os.path.join(ROOT, "api/_routes/hello/__init__.py"), "# package\n")

    # 7) api/_routes/hello/index.py
    write(
        os.path.join(ROOT, "api/_routes/hello/index.py"),
        """
        from fastapi import APIRouter
        router = APIRouter()

        @router.get("/")
        def hello():
            return {"message": "Hello from FastAPI!"}
        """,
    )

    # แสดงผลโครงสร้างที่สร้าง
    print("\n✅ Rebuilt minimal FastAPI structure for Vercel. Files created:\n")
    for p in [
        "requirements.txt",
        "vercel.json",
        "api/index.py",
        "api/_routes/index/__init__.py",
        "api/_routes/index/index.py",
        "api/_routes/hello/__init__.py",
        "api/_routes/hello/index.py",
    ]:
        print(" -", p)

    # ทำ git add/commit (ไม่ push ในสคริปต์เพื่อเลี่ยงกรณี remote ล้ำหน้า)
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(
            ["git", "commit", "-m", "Reset minimal FastAPI routes for Vercel (runtime python3.11)"],
            check=True,
        )
        print("\nℹ️  Commit เรียบร้อย — ต่อไปให้รันคำสั่ง push ด้านล่างด้วยตัวเอง:")
    except subprocess.CalledProcessError:
        print("\nℹ️  ไม่มีไฟล์เปลี่ยนแปลง หรือ commit ไม่สำเร็จ (ข้ามขั้นตอนนี้ได้)")

    print(
        textwrap.dedent(
            """
            ----------------------------------------------------------
            NEXT:
            1) ดึงของระยะไกลมาก่อน (กัน remote ล้ำหน้า)
               git pull --rebase origin main

            2) push ขึ้น GitHub เพื่อให้ Vercel deploy อัตโนมัติ
               git push origin main

            จากนั้นทดสอบ:
              /api         → https://o-onotty-oo99-alert.vercel.app/api
              /api/health  → https://o-onotty-oo99-alert.vercel.app/api/health
              /api/index   → https://o-onotty-oo99-alert.vercel.app/api/index
              /api/hello   → https://o-onotty-oo99-alert.vercel.app/api/hello
            ----------------------------------------------------------
            """
        )
    )

if __name__ == "__main__":
    sys.exit(main())
