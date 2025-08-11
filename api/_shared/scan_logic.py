# api/_shared/scan_logic.py
from __future__ import annotations

import os
import time
from typing import Any, Dict, Iterable, List

import requests


def scan_group(group: str) -> Dict[str, Any]:
    """
    สแกนกลุ่มทรัพย์สิน (ตัวอย่าง/สตับ) — แทนที่ด้วย logic จริงของคุณได้
    คืนค่าเป็น dict รูปแบบ:
    {
        "group": "<ชื่อกลุ่ม>",
        "ts": <unix time>,
        "items": [{"symbol": "...", "signal": "BUY|SELL|HOLD"}, ...]
    }
    """
    # จำลองเวลาในการประมวลผลเล็กน้อย
    time.sleep(0.5)

    # ตัวอย่าง mapping กลุ่ม -> รายชื่อสัญลักษณ์ (แก้ไขได้ตามจริง)
    preset: Dict[str, List[str]] = {
        "sp500": ["AAPL", "MSFT", "NVDA"],
        "nasdaq100": ["GOOGL", "META", "AMZN"],
        "bitkub": ["BTC_THB", "ETH_THB", "ARB_THB"],
        "set50": ["PTT", "SCB", "AOT"],
        "set100": ["ADVANC", "BDMS", "CPALL"],
        "etfs": ["SPY", "QQQ", "VTI"],
        "okx_top200": ["BTC", "ETH", "SOL"],
        "binance_top200": ["BNB", "ADA", "XRP"],
        "gold": ["XAUUSD"],
    }

    symbols = preset.get(group.lower(), ["DEMO1", "DEMO2"])

    # ตัวอย่างการสร้างสัญญาณอย่างง่าย (สลับ BUY/SELL/HOLD)
    items: List[Dict[str, Any]] = []
    for i, sym in enumerate(symbols):
        signal = "BUY" if i % 3 == 0 else ("SELL" if i % 3 == 1 else "HOLD")
        items.append({"symbol": sym, "signal": signal})

    return {"group": group, "ts": int(time.time()), "items": items}


def notify_telegram(text: str) -> bool:
    """
    ส่งข้อความไป Telegram โดยใช้ ENV: TG_BOT_TOKEN, TG_CHAT_ID
    คืนค่า True ถ้าส่งสำเร็จ / False ถ้าไม่ส่งหรือไม่มีการตั้งค่า
    """
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
        return r.ok
    except Exception:
        return False


def format_items_for_message(group: str, items: Iterable[Dict[str, Any]]) -> str:
    """
    ตัวช่วยสำหรับสร้างข้อความสรุปผลสแกน เพื่อส่งไป Telegram หรือแสดงผล
    """
    lines = [f"Scan results: {group}", "-" * 20]
    for it in items:
        lines.append(f"{it.get('symbol', '?')}: {it.get('signal', '-')}")
    return "\n".join(lines)
