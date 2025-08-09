# api/_shared/app_factory.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

def create_app() -> FastAPI:
    app = FastAPI()

    # ใส่โดเมนของหน้าเว็บ UI ของคุณที่เรียก API ได้จริง
    origins = [
        "https://signal-dashboard-ui.vercel.app",  # UI ที่รันบน Vercel
        "http://localhost:5173",                   # เผื่อทดสอบ local dev
    ]

    # เผื่ออยากเติมผ่าน ENV เพิ่มได้ (คั่นด้วย comma)
    extra = os.getenv("CORS_EXTRA_ORIGINS", "")
    if extra:
        origins += [o.strip() for o in extra.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],     # GET/POST/PUT/DELETE...
        allow_headers=["*"],
    )
    return app

