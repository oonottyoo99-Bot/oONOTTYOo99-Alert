# rebuild_api.py
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent

def rewrite(path: Path, content: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main():
    # 1) ล้าง api/ เดิมออกให้เกลี้ยง
    api_dir = ROOT / "api"
    if api_dir.exists():
        shutil.rmtree(api_dir)

    # 2) requirements.txt (ให้ FastAPI + Uvicorn)
    rewrite(
        ROOT / "requirements.txt",
        "fastapi>=0.110.0\nuvicorn[standard]>=0.27.0\n",
    )

    # 3) vercel.json – ระบุ runtime ของ python ให้ฟังก์ชันใน api/
    rewrite(
        ROOT / "vercel.json",
        '{\n'
        '  "functions": {\n'
        '    "api/**.py": { "runtime": "python3.11" }\n'
        '  }\n'
        '}\n'
    )

    # --------------------------
    # โครงสร้าง api/
    # --------------------------
    # api/__init__.py
    rewrite(ROOT / "api" / "__init__.py", "")

    # api/index.py (ตัวหลัก: FastAPI app, /, /health, include routers)
    rewrite(
        ROOT / "api" / "index.py",
        '''\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="oONOTTYOo99-Alert API")

# CORS (เปิดกว้างเพื่อทดสอบ)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True,
)

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

# รวม sub-routers (ใช้ absolute import)
try:
    from api._routes.index.index import router as index_router
    from api._routes.hello.index import router as hello_router

    app.include_router(index_router, prefix="/index")
    app.include_router(hello_router, prefix="/hello")

except Exception as e:
    # มี endpoint ให้เช็ค error import ได้ที่ /api/debug_import
    @app.get("/debug_import")
    def debug_import():
        return {"import_error": str(e)}
'''
    )

    # api/_routes/index/__init__.py
    rewrite(ROOT / "api" / "_routes" / "index" / "__init__.py", "")

    # api/_routes/index/index.py
    rewrite(
        ROOT / "api" / "_routes" / "index" / "index.py",
        '''\
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def index():
    return {"message": "This is index route"}
'''
    )

    # api/_routes/hello/__init__.py
    rewrite(ROOT / "api" / "_routes" / "hello" / "__init__.py", "")

    # api/_routes/hello/index.py
    rewrite(
        ROOT / "api" / "_routes" / "hello" / "index.py",
        '''\
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def hello():
    return {"message": "Hello from FastAPI!"}
'''
    )

    print("✅ Rebuilt /api for Vercel + FastAPI, files created:")
    for p in [
        "api/__init__.py",
        "api/index.py",
        "api/_routes/index/__init__.py",
        "api/_routes/index/index.py",
        "api/_routes/hello/__init__.py",
        "api/_routes/hello/index.py",
        "requirements.txt",
        "vercel.json",
    ]:
        print(" -", p)

if __name__ == "__main__":
    main()
