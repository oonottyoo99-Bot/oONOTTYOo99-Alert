# rebuild_api.py  — ล้าง api/ เดิมและสร้างใหม่ให้ Vercel เห็นแน่นอน
import os, shutil, textwrap, json, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.join(ROOT, "api")

def write(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).lstrip("\n"))

def main():
    # 1) ลบ api/ เก่าทิ้ง (ถ้ามี)
    if os.path.isdir(API_DIR):
        shutil.rmtree(API_DIR)

    # 2) เขียนโค้ดใหม่แบบขั้นต่ำสุดให้ใช้งานได้ทันที
    #    - api/index.py  (มี app = FastAPI())
    #    - api/index/index.py (router)
    #    - api/hello/index.py (router)
    #    - api/__init__.py , api/index/__init__.py , api/hello/__init__.py (ว่าง)
    write(os.path.join(API_DIR, "__init__.py"), "")

    write(os.path.join(API_DIR, "index.py"), """
        from fastapi import FastAPI, APIRouter

        app = FastAPI(title="Vercel + FastAPI minimal")

        @app.get("/")
        def root():
            return {
                "ok": True,
                "service": "oONOTTYOo99-Alert API",
                "routes": ["/api", "/api/health", "/api/index", "/api/hello"],
            }

        @app.get("/health")
        def health():
            return {"ok": True}

        # include sub-routers
        from .index.index import router as index_router
        from .hello.index import router as hello_router

        app.include_router(index_router, prefix="/index")
        app.include_router(hello_router,  prefix="/hello")
    """)

    # /api/index/
    write(os.path.join(API_DIR, "index", "__init__.py"), "")
    write(os.path.join(API_DIR, "index", "index.py"), """
        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/")
        def index():
            return {"message": "This is index route"}
    """)

    # /api/hello/
    write(os.path.join(API_DIR, "hello", "__init__.py"), "")
    write(os.path.join(API_DIR, "hello", "index.py"), """
        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/")
        def hello():
            return {"message": "Hello from FastAPI!"}
    """)

    # 3) vercel.json — บังคับ runtime ของไฟล์ python ใน /api ให้เป็น python3.11
    vercel_json_path = os.path.join(ROOT, "vercel.json")
    vercel_json = {
        "functions": {
            "api/**/*.py": { "runtime": "python3.11" }
        }
    }
    with open(vercel_json_path, "w", encoding="utf-8") as f:
        json.dump(vercel_json, f, indent=2)

    # 4) requirements.txt (ให้แน่ใจว่ามี fastapi ติดตั้งตอนรัน)
    req_path = os.path.join(ROOT, "requirements.txt")
    if not os.path.exists(req_path):
        write(req_path, """
            fastapi==0.110.0
        """)

    # 5) git add + commit (ถ้าต้องการให้ push เอง ให้ uncomment บรรทัด push)
    subprocess.run(["git", "add", "api", "vercel.json", "requirements.txt"], check=True)
    subprocess.run(["git", "commit", "-m", "Rebuild api/ with minimal FastAPI + vercel.json"], check=True)
    # subprocess.run(["git", "push"], check=True)

    print("✅ Rebuilt api/ and wrote vercel.json. Commit created.")
    print("👉 ตรวจใน Vercel > Deployments ให้เกิด deployment ใหม่จาก commit นี้")

if __name__ == "__main__":
    main()
