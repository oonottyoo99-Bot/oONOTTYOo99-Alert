# main.py (Dashboard-Ready Version)
import os
import yfinance as yf
import pandas as pd
import telegram
import asyncio
import json
import requests
from fastapi import FastAPI, Query
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
REPO_NAME = "oONOTTYOo99-Bot/oONOTTYOo99-Alert"

# --- ฟังก์ชันดึงรายชื่อสินทรัพย์แบบ Dynamic ---

def get_sp500_tickers():
    print("Fetching S&P 500 tickers...")
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        html = requests.get(url, timeout=15).content
        df = pd.read_html(html)[0]
        return [ticker.replace('.', '-') for ticker in df['Symbol'].tolist()]
    except Exception as e:
        print(f"Error fetching S&P 500: {e}"); return []

def get_nasdaq100_tickers():
    print("Fetching Nasdaq 100 tickers...")
    try:
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        html = requests.get(url, timeout=15).content
        df = pd.read_html(html)[4] # The 4th table on the page
        return [ticker.replace('.', '-') for ticker in df['Ticker'].tolist()]
    except Exception as e:
        print(f"Error fetching Nasdaq 100: {e}"); return []

def get_set_tickers(group):
    print(f"Fetching {group} tickers...")
    try:
        url = f'https://www.settrade.com/th/equities/market-data/set{group.split("SET")[1]}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find tickers from the specific table structure of settrade
        tickers = [a.text.strip() + ".BK" for a in soup.select('div.symbol-name a')]
        return tickers
    except Exception as e:
        print(f"Error fetching {group}: {e}"); return []

def get_crypto_tickers():
    print("Fetching Crypto tickers...")
    try:
        cg = CoinGeckoAPI()
        all_tickers = set()
        # Top 100 Altcoins
        top_101 = cg.get_coins_markets(vs_currency='usd', per_page=101, page=1)
        altcoins = {f"{c['symbol'].upper()}-USD" for c in top_101 if c['symbol'].lower() != 'btc'}
        all_tickers.update(altcoins)
        # Top Layer 2
        l2_data = cg.get_coins_by_category(category_id='layer-2')
        l2_tickers = {f"{c['symbol'].upper()}-USD" for c in l2_data[:20]}
        all_tickers.update(l2_tickers)
        # Layer 3 is not a standard category, so we skip it.
        return list(all_tickers)
    except Exception as e:
        print(f"Error fetching Crypto: {e}"); return []

def get_etf_tickers():
    return [
        "SPY", "IVV", "VTI", "VOO", "QQQ", "VEA", "VTV", "IEFA", "VUG", "AGG",
        "VWO", "BND", "IWM", "IWF", "EFA", "IJH", "IJR", "XLF", "VIG", "SCHD",
        "XLK", "XLY", "XLP", "XLE", "XLV", "XLI", "VGT", "VNQ", "DIA", "USO"
    ]

def get_gold_ticker():
    return ["GLD"]

# --- ฟังก์ชันคำนวณและสแกน (เหมือนเดิม) ---
# ... (วางฟังก์ชัน calculate_ema, calculate_sma, calculate_rsi, calculate_macd, send_telegram_message, analyze_ticker, update_signals_on_github ทั้งหมดไว้ที่นี่) ...
def calculate_ema(prices, length): return prices.ewm(span=length, adjust=False).mean()
def calculate_sma(data, length): return data.rolling(window=length).mean()
def calculate_rsi(prices, length=14):
    delta = prices.diff(); gain = (delta.where(delta > 0, 0)).rolling(window=length).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
    if loss.empty or loss.iloc[-1] == 0: return 100.0
    rs = gain / loss; return 100 - (100 / (1 + rs))
def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast, ema_slow = calculate_ema(prices, fast), calculate_ema(prices, slow); macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal); return macd_line, signal_line
async def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    try: bot = telegram.Bot(token=TELEGRAM_TOKEN); await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
    except Exception as e: print(f"Telegram Error: {e}")
async def analyze_ticker(ticker: str):
    try:
        data = yf.download(ticker, period="250d", interval=TIME_FRAME, progress=False, timeout=10);
        if data.empty or len(data) < 200: return None
        data['EMA100'] = calculate_ema(data['Close'], 100); data['EMA200'] = calculate_ema(data['Close'], 200)
        data['RSI_14'] = calculate_rsi(data['Close'], 14); data['MACD'], data['MACDs'] = calculate_macd(data['Close'])
        data['Volume_SMA20'] = calculate_sma(data['Volume'], 20); latest = data.iloc[-1]
        signal_info = { "ticker": ticker, "timeframe": TIME_FRAME, "price": f"{latest['Close']:.2f}" }
        is_volume_spike = latest['Volume'] > (latest['Volume_SMA20'] * VOLUME_MULTIPLIER)
        is_above_emas = latest['Close'] > latest['EMA100'] and latest['Close'] > latest['EMA200']
        is_rsi_strong = latest['RSI_14'] > 55; is_macd_positive = latest['MACD'] > latest['MACDs']
        if is_above_emas and is_rsi_strong and is_macd_positive and is_volume_spike:
            signal_info["signal"] = "Strong Buy"; await send_telegram_message(f"🚀 *Strong Buy Signal!*\n*{ticker}* ({TIME_FRAME})"); return signal_info
        if is_volume_spike:
            signal_info["signal"] = "Volume Spike"; await send_telegram_message(f"🔔 *Volume Spike Alert!*\n*{ticker}* ({TIME_FRAME})"); return signal_info
    except Exception as e: print(f"Analyze Error for {ticker}: {e}")
    return None
def update_signals_on_github(signals: list, group: str):
    if not GITHUB_TOKEN: print("GitHub Token not found."); return
    try:
        g = Github(GITHUB_TOKEN); repo = g.get_repo(REPO_NAME); utc_now = datetime.now(timezone.utc)
        bangkok_now = utc_now.astimezone(timezone(timedelta(hours=7)))
        content_to_write = {"last_updated": bangkok_now.strftime("%Y-%m-%d %H:%M:%S Bangkok"), "scan_group": group, "signals_found": signals}
        file_path = "signals.json"; json_content = json.dumps(content_to_write, indent=4)
        try: contents = repo.get_contents(file_path, ref="main"); repo.update_file(contents.path, f"Update signals for {group}", json_content, contents.sha, branch="main")
        except: repo.create_file(file_path, f"Create signals for {group}", json_content, branch="main")
        print(f"✅ Successfully updated/created {file_path} on GitHub.")
    except Exception as e: print(f"❌ GitHub update error: {e}")

# --- ฟังก์ชัน Run Scan ที่ถูกอัปเกรด ---
async def run_scan(group: str):
    print(f"--- Starting new scan cycle for group: {group} ---")
    
    tickers_to_scan = []
    if group == 'sp500': tickers_to_scan = get_sp500_tickers()
    elif group == 'nasdaq100': tickers_to_scan = get_nasdaq100_tickers()
    elif group == 'etf': tickers_to_scan = get_etf_tickers()
    elif group == 'crypto': tickers_to_scan = get_crypto_tickers()
    elif group == 'set50': tickers_to_scan = get_set_tickers('SET50')
    elif group == 'set100': tickers_to_scan = get_set_tickers('SET100')
    elif group == 'gold': tickers_to_scan = get_gold_ticker()
    else: print(f"Unknown group: {group}"); return

    if not tickers_to_scan: print(f"No tickers found for group: {group}"); return

    found_signals = []
    tasks = [analyze_ticker(ticker) for ticker in tickers_to_scan]
    results = await asyncio.gather(*tasks)
    
    for res in results:
        if res: found_signals.append(res)
            
    update_signals_on_github(found_signals, group)
    print(f"--- Scan cycle for {group} finished ---")

# --- Web Server ---
app = FastAPI()

@app.get("/")
def home(): return {"status": "Dashboard-Ready Scanner API is online."}

@app.get("/run_scan")
async def trigger_scan(group: str = Query(None)):
    if not group: return {"error": "Please provide a 'group' parameter."}
    
    # Run in background
    asyncio.create_task(run_scan(group))
    return {"status": f"Scan triggered for group '{group}' in the background."}
