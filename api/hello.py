from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"ok": True, "route": "/api/hello"}

@app.get("/health")
def health():
    return {"ok": True}
