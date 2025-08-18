import json
from datetime import datetime

def handler(request):
    body = {
        "ok": True,
        "service": "oONOTTYOo99-Alert (native python function)",
        "time": datetime.utcnow().isoformat() + "Z",
        "routes": ["/api"]  # ตอนนี้ทำ route เดียวให้ผ่านก่อน
    }
    return {
        "status": 200,
        "headers": {"content-type": "application/json; charset=utf-8"},
        "body": json.dumps(body)
    }
