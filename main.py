# main.py (Full System - Final Version)
import os
import yfinance as yf
import pandas as pd
import telegram
import asyncio
import json
import requests
from fastapi import FastAPI
from github import Github
from datetime import datetime, timezone, timedelta
from pycoingecko import CoinGeckoAPI
from bs4 import BeautifulSoup

# --- การตั้งค่า ---
VOLUME_MULTIPLIER = 2.0
TIME_FRAME = "1d"

# --- ดึงข้อมูลลับ ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "oONOTTYOo99-Bot/oONOTTYOo99-Alert" # ชื่อ repo ของคุณ

# --- ฟังก์ชันดึงรายชื่อสินทรัพย์แบบ Dynamic ---
def get_sp500_tickers():
    """Fetches S&P 500 tickers from Wikipedia."""
    print("Fetching S&P 500 tickers...")
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        html = requests.get(url, timeout=15).content
        df_list = pd.read_html(html)
        tickers = df_list[0]['Symbol'].tolist()
        # Replace dots with dashes for Yahoo Finance compatibility (e.g., BRK.B -> BRK-B)
        tickers = [ticker.replace('.', '-') for ticker in tickers]
        print(f"Found {len(tickers)} S&P 500 tickers.")
        return tickers
    except Exception as e:
        print(f"Could not fetch S&P 500 tickers: {e}")
        return []

def get_crypto_tickers():
    """Fetches crypto tickers from CoinGecko."""
    print("Fetching Crypto tickers from CoinGecko...")
    try:
        cg = CoinGeckoAPI()
        all_tickers = set()

        # Top 100 Altcoins (Top 101 and remove BTC)
        top_101 = cg.get_coins_markets(vs_currency='usd', per_page=101, page=1)
        altcoins = {f"{c['symbol'].upper()}-USD" for c in top_101 if c['symbol'].lower() != 'btc'}
        all_tickers.update(altcoins)
        print(f"Found {len(altcoins)} altcoins.")

        # Top 20 Layer 2
        l2_data = cg.get_coins_by_category(category_id='layer-2')
        l2_tickers = {f"{c['symbol'].upper()}-USD" for c in l2_data[:20]}
        all_tickers.update(l2_tickers)
        print(f"Found {len(l2_tickers)} Layer-2 coins.")

        print(f"Total unique crypto tickers: {len(all_tickers)}")
        return list(all_tickers)
    except Exception as e:
        print(f"Could not fetch Crypto tickers: {e}")
        return []

def get_etf_and_gold_tickers():
    """Returns a static list of major ETFs and Gold."""
    print("Getting ETF and Gold tickers...")
    etfs = [
        "SPY", "IVV", "VTI", "VOO", "QQQ", "VEA", "VTV", "IEFA", "VUG", "AGG",
        "VWO", "BND", "IWM", "IWF", "EFA", "IJH", "IJR", "XLF", "VIG", "GLD", # GLD for Gold
        "XLK", "XLY", "XLP", "XLE", "XLV", "XLI", "VGT", "SCHD", "DIA", "USO"
    ]
    print(f"Found {len(etfs)} ETF and Gold tickers.")
    return etfs

async def get_all_tickers_to_scan():
    """Builds the full list of assets to scan."""
    print("--- Building full list of assets to scan ---")
    sp500 = get_sp500_tickers()
    crypto = get_crypto_tickers()
    etfs = get_etf_and_gold_tickers()

    full_list = set(sp500 + crypto + etfs)
    print(f"--- Total unique assets to scan: {len(full_list)} ---")
    return list(full_list)

# --- ฟังก์ชันคำนวณและสแกน ---
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
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    return macd_line, signal_line

async def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
    except Exception as e:
        print(f"Telegram Error: {e}")

async def analyze_ticker(ticker: str):
    try:
        data = yf.download(ticker, period="250d", interval=TIME_FRAME, progress=False, timeout=10)
        if data.empty or len(data) < 200:
            print(f"Not enough data for {ticker}, skipping.")
            return None

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
            await send_telegram_message(f"🚀 *Strong Buy Signal!*\n*{ticker}* ({TIME_FRAME})")
            return signal_info
            
        if is_volume_spike:
            signal_info["signal"] = "Volume Spike"
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
    tickers_to_scan = await get_all_tickers_to_scan()
    
    found_signals = []
    tasks = [analyze_ticker(ticker) for ticker in tickers_to_scan]
    results = await asyncio.gather(*tasks)
    
    for res in results:
        if res:
            found_signals.append(res)
            
    update_signals_on_github(found_signals)
    if not found_signals:
        print("No new signals found in this cycle.")
    print("--- Scan cycle finished ---")

# --- Web Server ---
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Full System Scanner API is online."}

@app.get("/run_scan")
async def trigger_scan():
    asyncio.create_task(run_scan())
    return {"status": "Full scan triggered in background. This may take several minutes."}
