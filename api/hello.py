def handler(request):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": '{"ok": true, "route": "/api/hello", "version": 1}'
    }
