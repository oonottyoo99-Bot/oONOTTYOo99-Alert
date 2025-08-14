from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def ping():
    return {"ok": True, "service": "oONOTTYOo99-Alert"}

