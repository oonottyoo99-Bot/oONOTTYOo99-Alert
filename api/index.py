from fastapi import FastAPI

app = FastAPI()

@app.get("/api/index")
def index():
    return {"message": "This is index route"}
