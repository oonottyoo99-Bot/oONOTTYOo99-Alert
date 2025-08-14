# /api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# สร้าง FastAPI app (Vercel ต้องเห็นชื่อตัวแปรว่า "app")
app = FastAPI(title="oONOTTYOo99-Alert API")

# อนุญาต CORS แบบกว้าง (ปรับทีหลังได้)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ---- root ของ /api ----
@app.get("/")
def api_root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": [
            "/api",
            "/api/hello",
            "/api/hello/health",
        ],
    }

# ---- include routers ย่อย ----
# หมายเหตุ: ไฟล์นี้คาดว่าอยู่ที่ /api/hello.py และมีตัวแปรชื่อ "router"
from hello import router as hello_router  # noqa: E402

app.include_router(hello_router, prefix="/hello", tags=["hello"])
