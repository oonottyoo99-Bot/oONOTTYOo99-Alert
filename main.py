# main.py (เวอร์ชัน Hybrid สำหรับ Web Service + Scanner)
import os
import yfinance as yf
import pandas_ta as ta
import telegram
import asyncio
from fastapi import FastAPI
from typing import List

# --- การตั้งค่าเริ่มต้น ---
# กลุ่มสินทรัพย์ทั้งหมดที่เรามี
TICKER_GROUPS = {
    "us_stocks": ["AAPL", "AMZN", "GOOGL", "NVDA", "META", "MSFT", "TSLA"],
    "crypto": ["BTC-USD", "ETH-USD"], # Ticker คู่เงิน USDT ไม่รองรับใน yfinance
    "etf": ["MSTY", "SCHD", "QQQ", "JEPQ"],
    "gold": ["GLD"],
    # คุณสามารถเพิ่มกลุ่มอื่นๆ ได้ที่นี่
}

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
            await send_telegram_message(f"🔔 *Volume Spike Alert!*\\n*{ticker}* ({TIME_FRAME})")

        is_above_emas = latest['Close'] > latest['EMA100'] and latest['Close'] > latest['EMA200']
        is_rsi_strong = latest['RSI_14'] > 55
        is_macd_positive = latest['MACD'] > latest['MACDs']
        
        if is_above_emas and is_rsi_strong and is_macd_positive and is_volume_spike:
            await send_telegram_message(f"🚀 *Strong Buy Signal!*\\n*{ticker}* ({TIME_FRAME})\\nราคา: {latest['Close']:.2f}")

    except Exception as e:
        print(f"เกิดข้อผิดพลาดระหว่างวิเคราะห์ {ticker}: {e}")

async def run_scan(tickers: List[str]):
    """ฟังก์ชันหลักที่จะถูกเรียกให้ทำงานเบื้องหลัง"""
    print(f"--- เริ่มการสแกนรอบใหม่สำหรับกลุ่ม: {tickers} ---")
    await asyncio.gather(*(analyze_ticker(t) for t in tickers))
    print("--- การสแกนเสร็จสิ้น ---")

# --- ส่วนของ Web Server ---
app = FastAPI()

@app.get("/")
def home():
    return {"status": "API is online and ready."}

@app.get("/scan/{group_name}")
async def trigger_scan(group_name: str):
    """Endpoint ที่ให้หน้าเว็บเรียกเพื่อสั่งสแกนตามกลุ่ม"""
    tickers_to_scan = TICKER_GROUPS.get(group_name.lower())
    if not tickers_to_scan:
        return {"status": "error", "message": f"ไม่พบกลุ่มสินทรัพย์ชื่อ '{group_name}'"}
    
    print(f"Scan triggered by external job for group: {group_name}")
    asyncio.create_task(run_scan(tickers_to_scan))
    
    return {"status": "success", "message": f"Scan for group '{group_name}' triggered successfully in the background."}
