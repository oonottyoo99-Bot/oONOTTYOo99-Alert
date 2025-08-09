# api/_shared/scan_logic.py
import os
import time
import requests

def scan_group(group: str):
    """
    ปรับเป็นลอจิกจริงของคุณ: ดึงข้อมูล/สแครป/คำนวณสัญญาณ ฯลฯ
    ตอนนี้ทำ mock ไว้เป็นตัวอย่าง
    """
    time.sleep(1.0)  # จำลองใช้เวลา
    return {
        "group": group,
        "ts": int(time.time()),
        "items": [
            {"symbol": "AAPL", "signal": "BUY"},
            {"symbol": "MSFT", "signal": "HOLD"},
        ],
    }

def notify_telegram(text: str):
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    if not (token and chat_id):
        return  # ไม่ตั้งค่า ก็ข้ามไป
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception:
        pass

