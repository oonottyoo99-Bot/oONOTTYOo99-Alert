# api/_shared/app_factory.py
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

def create_app(router: APIRouter) -> FastAPI:
    app = FastAPI()
    # CORS เปิดกว้างก่อน ช่วงทดสอบ
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    # mount router ที่ path รากของฟังก์ชันย่อยนั้นๆ
    app.include_router(router, prefix="")
    return app
