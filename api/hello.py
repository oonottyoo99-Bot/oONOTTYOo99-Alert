import json

def handler(request):
    body = {"ok": True, "route": "/api/hello"}
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

