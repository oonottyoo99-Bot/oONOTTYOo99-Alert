from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def hello():
    return jsonify(ok=True, route="/api/hello")
