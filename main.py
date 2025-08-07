# main.py (เวอร์ชันสุดท้าย - ไม่ใช้ pandas-ta)
import os
import yfinance as yf
import pandas as pd
import telegram
import asyncio
from fastapi import FastAPI

# --- ตั้งค่าเริ่มต้น ---
TICKERS_TO_SCAN = [
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD",
    "SPY", "QQQ", "VOO",
    "AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"
]
VOLUME_MULTIPLIER = 2.0
TIME_FRAME = "1d"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- ฟังก์ชันคำนวณ Indicator ของเราเอง ---

def calculate_ema(prices, length):
    return prices.ewm(span=length, adjust=False).mean()

def calculate_sma(data, length):
    return data.rolling(window=length).mean()

def calculate_rsi(prices, length=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    return macd_line, signal_line

# --- ส่วนของการสแกนและส่งข้อความ ---

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
        data = yf.download(ticker, period="250d", interval=TIME_FRAME, progress=False)
        if data.empty: return

        # คำนวณ Indicators ด้วยฟังก์ชันของเราเอง
        data['EMA100'] = calculate_ema(data['Close'], 100)
        data['EMA200'] = calculate_ema(data['Close'], 200)
        data['RSI_14'] = calculate_rsi(data['Close'], 14)
        data['MACD'], data['MACDs'] = calculate_macd(data['Close'])
        data['Volume_SMA20'] = calculate_sma(data['Volume'], 20)
        
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
    print("--- เริ่มการสแกนรอบใหม่ ---")
    for ticker in TICKERS_TO_SCAN:
        await analyze_ticker(ticker)
    print("--- การสแกนเสร็จสิ้น ---")

# --- ส่วนของ Web Server ---
app = FastAPI()

@app.get("/")
def home():
    return {"status": "API is online. Ready to be triggered."}

@app.get("/run_scan")
async def trigger_scan():
    print("Scan triggered by external job.")
    asyncio.create_task(run_scan())
    return {"status": "Scan triggered successfully in the background."}
