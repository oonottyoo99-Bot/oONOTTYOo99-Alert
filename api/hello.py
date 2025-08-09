from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        body = {"ok": True, "route": "/api/hello"}
        self.wfile.write(json.dumps(body).encode("utf-8"))
