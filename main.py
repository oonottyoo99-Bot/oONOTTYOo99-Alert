# main.py (เวอร์ชัน Final v2 - แก้ไข PyGithub)
import os
import yfinance as yf
import pandas as pd
import telegram
import asyncio
import json
from fastapi import FastAPI
from github import Github # <<< แก้ไข: เอา InputFile ออก
from datetime import datetime, timezone, timedelta

# --- การตั้งค่า ---
TICKERS_TO_SCAN = [
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD",
    "SPY", "QQQ", "VOO", "ARKK",
    "AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN"
]
VOLUME_MULTIPLIER = 2.0
TIME_FRAME = "1d"

# --- ดึงข้อมูลลับ ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "oONOTTYOo99-Bot/oONOTTYOo99-Alert" # เปลี่ยนเป็นชื่อ repo ของคุณ

# --- ฟังก์ชันคำนวณ (เหมือนเดิม) ---
def calculate_ema(prices, length): return prices.ewm(span=length, adjust=False).mean()
def calculate_sma(data, length): return data.rolling(window=length).mean()
def calculate_rsi(prices, length=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
    if loss.empty or loss.iloc[-1] == 0: return 100.0
    rs = gain / loss
    return 100 - (100 / (1 + rs))
def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast, ema_slow = calculate_ema(prices, fast), calculate_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    return macd_line, signal_line

# --- ฟังก์ชันหลัก ---
async def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
    except Exception as e:
        print(f"Telegram Error: {e}")

async def analyze_ticker(ticker: str):
    try:
        data = yf.download(ticker, period="250d", interval=TIME_FRAME, progress=False)
        if data.empty: return None

        data['EMA100'] = calculate_ema(data['Close'], 100)
        data['EMA200'] = calculate_ema(data['Close'], 200)
        data['RSI_14'] = calculate_rsi(data['Close'], 14)
        data['MACD'], data['MACDs'] = calculate_macd(data['Close'])
        data['Volume_SMA20'] = calculate_sma(data['Volume'], 20)

        latest = data.iloc[-1]
        signal_info = { "ticker": ticker, "timeframe": TIME_FRAME, "price": f"{latest['Close']:.2f}" }

        is_volume_spike = latest['Volume'] > (latest['Volume_SMA20'] * VOLUME_MULTIPLIER)
        is_above_emas = latest['Close'] > latest['EMA100'] and latest['Close'] > latest['EMA200']
        is_rsi_strong = latest['RSI_14'] > 55
        is_macd_positive = latest['MACD'] > latest['MACDs']

        if is_above_emas and is_rsi_strong and is_macd_positive and is_volume_spike:
            signal_info["signal"] = "Strong Buy"
            signal_info["details"] = "Price above EMAs, RSI > 55, MACD crossover, with Volume Spike."
            await send_telegram_message(f"🚀 *Strong Buy Signal!*\n*{ticker}* ({TIME_FRAME})")
            return signal_info

        if is_volume_spike:
            signal_info["signal"] = "Volume Spike"
            signal_info["details"] = "Volume is significantly higher than 20-period average."
            await send_telegram_message(f"🔔 *Volume Spike Alert!*\n*{ticker}* ({TIME_FRAME})")
            return signal_info

    except Exception as e:
        print(f"Analyze Error for {ticker}: {e}")
    return None

def update_signals_on_github(signals: list):
    if not GITHUB_TOKEN:
        print("GitHub Token not found. Skipping file update.")
        return
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)

        utc_now = datetime.now(timezone.utc)
        bangkok_now = utc_now.astimezone(timezone(timedelta(hours=7)))

        content_to_write = {
            "last_updated": bangkok_now.strftime("%Y-%m-%d %H:%M:%S Bangkok"),
            "signals_found": signals
        }

        file_path = "signals.json"
        json_content = json.dumps(content_to_write, indent=4)

        try:
            contents = repo.get_contents(file_path, ref="main")
            repo.update_file(contents.path, f"Update signals {bangkok_now.isoformat()}", json_content, contents.sha, branch="main")
            print(f"✅ Successfully updated {file_path} on GitHub.")
        except:
            repo.create_file(file_path, f"Create signals {bangkok_now.isoformat()}", json_content, branch="main")
            print(f"✅ Successfully created {file_path} on GitHub.")

    except Exception as e:
        print(f"❌ GitHub update error: {e}")

async def run_scan():
    print("--- Starting new scan cycle ---")
    found_signals = []
    tasks = [analyze_ticker(ticker) for ticker in TICKERS_TO_SCAN]
    results = await asyncio.gather(*tasks)

    for res in results:
        if res:
            found_signals.append(res)

    # แก้ไข: เปลี่ยนเงื่อนไขเป็น 'if found_signals:' เพื่อให้สร้างไฟล์ว่างถ้าไม่เจอสัญญาณ
    update_signals_on_github(found_signals)
    if not found_signals:
        print("No new signals found in this cycle.")

    print("--- Scan cycle finished ---")

# --- Web Server ---
