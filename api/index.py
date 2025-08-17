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
