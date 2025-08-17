# rebuild_api.py
import os, shutil, pathlib, textwrap

ROOT = pathlib.Path(__file__).parent.resolve()
API_DIR = ROOT / "api"

def write(path: pathlib.Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

def main():
    # 1) ลบโฟลเดอร์ api/ เดิมทั้งหมด เพื่อเคลียร์ของเก่า
    if API_DIR.exists():
        shutil.rmtree(API_DIR)

    # 2) สร้างโครงใหม่แบบที่ Vercel ต้องการ (หนึ่งไฟล์ต่อหนึ่ง endpoint)
    #    - /api/index.py    -> GET /api
    #    - /api/health.py   -> GET /api/health
    #    - /api/hello.py    -> GET /api/hello
    write(API_DIR / "__init__.py", "# marker\n")

    write(API_DIR / "index.py", """
    from fastapi import FastAPI

    app = FastAPI(title="API root")

    @app.get("/")
    def root():
        return {"ok": True, "service": "oONOTTYOo99-Alert API", "routes": ["/api", "/api/health", "/api/hello"]}
    """)

    write(API_DIR / "health.py", """
    from fastapi import FastAPI

    app = FastAPI(title="Health")

    @app.get("/")
    def health():
        return {"ok": True}
    """)

    write(API_DIR / "hello.py", """
    from fastapi import FastAPI

    app = FastAPI(title="Hello")

    @app.get("/")
    def hello():
        return {"message": "Hello from FastAPI!"}
    """)

    # 3) (แนะนำ) ใส่ vercel.json บอก runtime ของฟังก์ชัน Python ให้ชัด
    write(ROOT / "vercel.json", """
    {
      "functions": {
        "api/*.py": {
          "runtime": "python3.11"
        }
      }
    }
    """)

    # 4) (สำคัญ) ให้แน่ใจว่ามี requirements.txt ที่ root
    #    ถ้าไฟล์คุณมีอยู่แล้ว จะไม่เขียนทับ; ถ้ายังไม่มี จะสร้างให้
    req = ROOT / "requirements.txt"
    if not req.exists():
        write(req, """
        fastapi>=0.110.0
        uvicorn[standard]>=0.27.0
        """)
    print("✅ Rebuilt /api for Vercel + FastAPI")

if __name__ == "__main__":
    main()
