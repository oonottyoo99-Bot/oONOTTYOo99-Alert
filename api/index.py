# /api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hello import router as hello_router
from ping import router as ping_router
from results import router as results_router
from scan import router as scan_router

app = FastAPI(title="oONOTTYOo99-Alert API")

# CORS
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
        "routes": [
            "/api",
            "/api/hello",
            "/api/ping",
            "/api/results",
            "/api/scan",
        ],
    }

# รวม router จากไฟล์อื่น
app.include_router(hello_router, prefix="/hello")
app.include_router(ping_router, prefix="/ping")
app.include_router(results_router, prefix="/results")
app.include_router(scan_router, prefix="/scan")
