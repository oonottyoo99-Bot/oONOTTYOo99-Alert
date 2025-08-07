# main.py (เวอร์ชัน Hybrid สำหรับ Web Service + Scanner)
import os
import yfinance as yf
import pandas_ta as ta
import telegram
import asyncio
from fastapi import FastAPI

# --- ตั้งค่าเริ่มต้น (เหมือนเดิม) ---
TICKERS_TO_SCAN = [
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD",
    "SPY", "QQQ", "VOO",
    "AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"
]
VOLUME_MULTIPLIER = 2.0
TIME_FRAME = "1d"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- ส่วนของการสแกน (เหมือนเดิม) ---
async def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: ไม่ได้ตั้งค่า TELEGRAM_TOKEN หรือ TELEGRAM_CHAT_ID")
        return
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        print(f"✅ ส่งข้อความสำเร็จ: {message}")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการส่งข้อความ: {e}")

async def analyze_ticker(ticker: str):
    print(f"--- กำลังวิเคราะห์ {ticker} ---")
    try:
        data = yf.download(ticker, period="200d", interval=TIME_FRAME, progress=False)
        if data.empty: return

        data.ta.ema(length=100, append=True, col_names=('EMA100'))
        data.ta.ema(length=200, append=True, col_names=('EMA200'))
        data.ta.rsi(length=14, append=True, col_names=('RSI_14'))
        data.ta.macd(fast=12, slow=26, signal=9, append=True, col_names=('MACD', 'MACDh', 'MACDs'))
        data.ta.sma(length=20, close='Volume', append=True, col_names=('Volume_SMA20'))
        
        latest = data.iloc[-1]
        
        is_volume_spike = latest['Volume'] > (latest['Volume_SMA20'] * VOLUME_MULTIPLIER)
        if is_volume_spike:
            await send_telegram_message(f"🔔 *Volume Spike Alert!*\n*{ticker}* ({TIME_FRAME})")

        is_above_emas = latest['Close'] > latest['EMA100'] and latest['Close'] > latest['EMA200']
        is_rsi_strong = latest['RSI_14'] > 55
        is_macd_positive = latest['MACD'] > latest['MACDs']
        
        if is_above_emas and is_rsi_strong and is_macd_positive and is_volume_spike:
            await send_telegram_message(f"🚀 *Strong Buy Signal!*\n*{ticker}* ({TIME_FRAME})\nราคา: {latest['Close']:.2f}")

    except Exception as e:
        print(f"เกิดข้อผิดพลาดระหว่างวิเคราะห์ {ticker}: {e}")

async def run_scan():
    """ฟังก์ชันหลักที่จะถูกเรียกให้ทำงานเบื้องหลัง"""
    print("--- เริ่มการสแกนรอบใหม่ ---")
    for ticker in TICKERS_TO_SCAN:
        await analyze_ticker(ticker)
    print("--- การสแกนเสร็จสิ้น ---")

# --- ส่วนของ Web Server (ส่วนใหม่) ---
app = FastAPI()

@app.get("/")
def home():
    """หน้าหลักของเว็บ แสดงข้อความว่าพร้อมทำงาน"""
    return {"status": "API is online and ready. The real work happens at /run_scan."}

@app.get("/run_scan")
async def trigger_scan():
    """
    Endpoint ที่จะให้ cron-job.org เข้ามาเรียก (ปลุก)
    เมื่อถูกเรียก จะสั่งให้ run_scan() ทำงานเบื้องหลัง
    และตอบกลับทันทีเพื่อไม่ให้ตัวปลุกต้องรอนาน
    """
    print("Scan triggered by external job.")
    # สั่งให้การสแกนทำงานเบื้องหลัง
    asyncio.create_task(run_scan())
    # ตอบกลับทันที
    return {"status": "Scan triggered successfully in the background."}
