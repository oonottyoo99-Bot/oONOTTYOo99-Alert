from fastapi import FastAPI, APIRouter

app = FastAPI(title="oONOTTYOo99-Alert API")

@app.get("/")
def root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": ["/api", "/api/health", "/api/hello"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

hello = APIRouter()
@hello.get("/")
def say_hello():
    return {"message": "Hello from FastAPI on Vercel!"}

app.include_router(hello, prefix="/hello")
