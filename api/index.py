from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="oONOTTYOo99-Alert API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
def root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API",
        "routes": ["/api", "/api/health", "/api/hello"]
    }

@app.get("/health")
def health():
    return {"ok": True}

# sub-router 'hello'
from fastapi import APIRouter
hello = APIRouter()

@hello.get("/")
def say_hello():
    return {"message": "Hello from FastAPI on Vercel!"}

app.include_router(hello, prefix="/hello")
