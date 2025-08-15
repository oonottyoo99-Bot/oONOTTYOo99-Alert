# rebuild_api.py
from pathlib import Path
import shutil
import textwrap

ROOT = Path(__file__).parent.resolve()
API = ROOT / "api"

# --------------------------
# 1) ลบของเก่าทั้งหมดใต้ /api
# --------------------------
if API.exists():
    shutil.rmtree(API)

# --------------------------
# 2) สร้างโครงสร้างโฟลเดอร์ใหม่
# --------------------------
# api/
# ├── __init__.py
# ├── index.py                 (FastAPI app หลัก)
# └── _routes/
#     ├── __init__.py
#     ├── index/
#     │   ├── __init__.py
#     │   └── index.py         (GET /api/index)
#     └── hello/
#         ├── __init__.py
#         └── index.py         (GET /api/hello)

(API / "_routes" / "index").mkdir(parents=True, exist_ok=True)
(API / "_routes" / "hello").mkdir(parents=True, exist_ok=True)

# --------------------------
# 3) เนื้อหาไฟล์ต่างๆ
# --------------------------
files = {
    API / "__init__.py": "",
    API / "index.py": textwrap.dedent(
        """
        # /api/index.py  (FastAPI main app)
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI(title="oONOTTYOo99-Alert API")

        # CORS กว้างๆ เพื่อความสะดวกตอนทดสอบ
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
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

        # ---- include sub-routers (absolute imports สำคัญมากเวลา deploy บน Vercel) ----
        from api._routes.index.index import router as index_router  # noqa: E402
        from api._routes.hello.index import router as hello_router  # noqa: E402

        app.include_router(index_router, prefix="/index")  # -> GET /api/index/
        app.include_router(hello_router, prefix="/hello")  # -> GET /api/hello/
        """
    ).strip()
    + "\n",
    API / "_routes" / "__init__.py": "",
    API / "_routes" / "index" / "__init__.py": "",
    API / "_routes" / "index" / "index.py": textwrap.dedent(
        """
        # /api/_routes/index/index.py
        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/")
        def index():
            return {"message": "This is index route"}
        """
    ).strip()
    + "\n",
    API / "_routes" / "hello" / "__init__.py": "",
    API / "_routes" / "hello" / "index.py": textwrap.dedent(
        """
        # /api/_routes/hello/index.py
        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/")
        def hello():
            return {"message": "Hello from FastAPI!"}
        """
    ).strip()
    + "\n",
}

# --------------------------
# 4) เขียนไฟล์ทั้งหมด
# --------------------------
created = []
for path, content in files.items():
    path.write_text(content, encoding="utf-8")
    created.append(str(path.relative_to(ROOT)))

# --------------------------
# 5) สรุปผล
# --------------------------
print("✅ Rebuilt /api for Vercel + FastAPI, files created:")
for p in created:
    print(" -", p)
print("\nNext:")
print("  1) Commit & Push ขึ้น GitHub")
print("  2) รอ Vercel deploy แล้วทดสอบ:")
print("     • GET /api          -> service/routes")
print("     • GET /api/health   -> {\"ok\": true}")
print("     • GET /api/index    -> {\"message\": \"This is index route\"}")
print("     • GET /api/hello    -> {\"message\": \"Hello from FastAPI!\"}")
