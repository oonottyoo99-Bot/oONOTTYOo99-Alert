# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

app = FastAPI(title="oONOTTYOo99-Alert API (minimal)")

# CORS (ผ่อนคลายไว้ก่อน)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], allow_credentials=True,
)

# --- root ของแอป (จะกลายเป็น /api บน Vercel) ---
@app.get("/")
def api_root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": ["/api", "/api/health", "/api/index", "/api/hello"]
    }

# --- health ---
@app.get("/health")
def api_health():
    return {"ok": True}

# --- /api/index ---
index_router = APIRouter()
@index_router.get("/")
def index():
    return {"message": "This is index route"}
app.include_router(index_router, prefix="/index")

# --- /api/hello ---
hello_router = APIRouter()
@hello_router.get("/")
def hello():
    return {"message": "Hello from FastAPI!"}
app.include_router(hello_router, prefix="/hello")
