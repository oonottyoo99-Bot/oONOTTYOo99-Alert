# rebuild_api.py  — wipe & scaffold a minimal FastAPI /api for Vercel

import os
import shutil
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent
API_DIR = ROOT / "api"
REQ = ROOT / "requirements.txt"

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")

def ensure_requirements():
    base = "fastapi>=0.110.0\nuvicorn[standard]>=0.27.0\n"
    if not REQ.exists():
        REQ.write_text(base, encoding="utf-8")
        return
    txt = REQ.read_text(encoding="utf-8")
    need = []
    if "fastapi" not in txt:
        need.append("fastapi>=0.110.0")
    if "uvicorn" not in txt:
        need.append("uvicorn[standard]>=0.27.0")
    if need:
        REQ.write_text(txt.rstrip() + "\n" + "\n".join(need) + "\n", encoding="utf-8")

def rebuild_api():
    # 1) remove old /api
    if API_DIR.exists():
        shutil.rmtree(API_DIR)

    # 2) create fresh functions

    # /api  -> /api index function
    write(API_DIR / "index.py", """
        from fastapi import FastAPI

        app = FastAPI(title="oONOTTYOo99-Alert API (root)")

        @app.get("/")
        def root():
            return {
                "ok": True,
                "service": "oONOTTYOo99-Alert API",
                "routes": [
                    "/api",
                    "/api/health",
                    "/api/hello",
                    "/api/ping",
                ],
            }
    """)

    # /api/health
    write(API_DIR / "health.py", """
        from fastapi import FastAPI
        app = FastAPI()

        @app.get("/")
        def health():
            return {"ok": True}
    """)

    # /api/hello
    write(API_DIR / "hello.py", """
        from fastapi import FastAPI
        app = FastAPI()

        @app.get("/")
        def hello():
            return {"message": "Hello from FastAPI!"}
    """)

    # /api/ping
    write(API_DIR / "ping.py", """
        from fastapi import FastAPI
        app = FastAPI()

        @app.get("/")
        def ping():
            return {"ok": True, "endpoint": "/api/ping"}
    """)

    print("✅ Rebuilt /api for Vercel + FastAPI, files created:")
    for p in sorted(API_DIR.rglob("*.py")):
        print(" -", p.relative_to(ROOT))

if __name__ == "__main__":
    ensure_requirements()
    rebuild_api()
