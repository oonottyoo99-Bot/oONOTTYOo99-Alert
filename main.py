# main.py (V5 - With Auto-Scan Settings)
import os
import yfinance as yf
import pandas as pd
import telegram
import asyncio
import json
import requests
import ccxt
from fastapi import FastAPI, Query, Body
from github import Github
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

# --- การตั้งค่า ---
VOLUME_MULTIPLIER = 2.0
TIME_FRAME = "1d"

# --- ดึงข้อมูลลับ ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "oONOTTYOo99-Bot/oONOTTYOo99-Alert"

# --- ฟังก์ชันดึงรายชื่อสินทรัพย์ (เหมือนเดิม) ---
def get_exchange_top_tickers(exchange_name, limit=200):
    print(f"Fetching Top {limit} tickers from {exchange_name.capitalize()}...")
    try:
        exchange = getattr(ccxt, exchange_name)(); markets = exchange.fetch_markets()
        usdt_pairs = [m for m in markets if m['quote'] == 'USDT' and m.get('active', True)]
        tickers_data = exchange.fetch_tickers([m['symbol'] for m in usdt_pairs])
        sorted_tickers = sorted(tickers_data.values(), key=lambda t: t.get('quoteVolume', 0), reverse=True)
        yfinance_tickers = [f"{t['symbol'].split('/')[0]}-USD" for t in sorted_tickers[:limit]]
        print(f"Found {len(yfinance_tickers)} tickers from {exchange_name.capitalize()}.")
        return yfinance_tickers
    except Exception as e: print(f"Error fetching from {exchange_name}: {e}"); return []
def get_sp500_tickers():
    print("Fetching S&P 500 tickers..."); try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'; html = requests.get(url, timeout=15).content
        df = pd.read_html(html)[0]; return [ticker.replace('.', '-') for ticker in df['Symbol'].tolist()]
    except Exception as e: print(f"Error fetching S&P 500: {e}"); return []
def get_nasdaq100_tickers():
    print("Fetching Nasdaq 100 tickers..."); try:
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'; html = requests.get(url, timeout=15).content
        df = pd.read_html(html)[4]; return [ticker.replace('.', '-') for ticker in df['Ticker'].tolist()]
    except Exception as e: print(f"Error fetching Nasdaq 100: {e}"); return []
def get_set_tickers(group):
    print(f"Fetching {group} tickers..."); try:
        url = f'https://www.settrade.com/th/equities/market-data/set{group.split("SET")[1]}'
        headers = {'User-Agent': 'Mozilla/5.0'}; response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser'); return [a.text.strip() + ".BK" for a in soup.select('div.symbol-name a')]
    except Exception as e: print(f"Error fetching {group}: {e}"); return []
def get_etf_tickers(): return ["SPY", "IVV", "VTI", "VOO", "QQQ", "VEA", "VTV", "IEFA", "VUG", "AGG", "VWO", "BND", "IWM", "IWF", "EFA", "IJH", "IJR", "XLF", "VIG", "SCHD", "XLK", "XLY", "XLP", "XLE", "XLV", "XLI", "VGT", "VNQ", "DIA", "USO"]
def get_gold_ticker(): return ["GLD"]

# --- ฟังก์ชันคำนวณและสแกน (เหมือนเดิม) ---
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
def update_json_on_github(file_path: str, content_to_write: dict, commit_message: str):
    if not GITHUB_TOKEN: print("GitHub Token not found."); return
    try:
        g = Github(GITHUB_TOKEN); repo = g.get_repo(REPO_NAME)
        json_content = json.dumps(content_to_write, indent=4)
        try:
            contents = repo.get_contents(file_path, ref="main")
            repo.update_file(contents.path, commit_message, json_content, contents.sha, branch="main")
        except:
            repo.create_file(file_path, commit_message, json_content, branch="main")
        print(f"✅ Successfully updated/created {file_path} on GitHub.")
    except Exception as e: print(f"❌ GitHub update error for {file_path}: {e}")

async def run_scan(group: str):
    print(f"--- Starting new scan cycle for group: {group} ---")
    tickers_map = {
        'sp500': get_sp500_tickers, 'nasdaq100': get_nasdaq100_tickers,
        'etf': get_etf_tickers, 'altcoins': lambda: get_exchange_top_tickers('okx'),
        'binance': lambda: get_exchange_top_tickers('binance'), 'okx': lambda: get_exchange_top_tickers('okx'),
        'bitkub': lambda: get_exchange_top_tickers('bitkub'), 'set50': lambda: get_set_tickers('SET50'),
        'set100': lambda: get_set_tickers('SET100'), 'gold': get_gold_ticker
    }
    if group not in tickers_map: print(f"Unknown group: {group}"); return
    
    tickers_to_scan = tickers_map[group]()
    if not tickers_to_scan: print(f"No tickers found for group: {group}"); return

    found_signals = [res for res in await asyncio.gather(*[analyze_ticker(t) for t in tickers_to_scan]) if res]
    
    bangkok_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=7)))
    update_json_on_github(
        "signals.json",
        {"last_updated": bangkok_now.strftime("%Y-%m-%d %H:%M:%S Bangkok"), "scan_group": group, "signals_found": found_signals},
        f"Update signals for {group}"
    )
    print(f"--- Scan cycle for {group} finished ---")

app = FastAPI()

@app.get("/")
def home(): return {"status": "Dashboard-Ready Scanner API is online."}

@app.post("/save_settings")
async def save_settings(settings: dict = Body(...)):
    print(f"Received settings to save: {settings}")
    bangkok_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=7)))
    content = {
        "last_updated": bangkok_now.strftime("%Y-%m-%d %H:%M:%S Bangkok"),
        "auto_scan_groups": settings.get("auto_scan_groups", [])
    }
    update_json_on_github("settings.json", content, "Update auto-scan settings")
    return {"status": "Settings saved successfully."}

@app.get("/run_scan")
async def trigger_scan(group: str = Query(None)):
    if group: # Manual scan from dashboard button
        asyncio.create_task(run_scan(group))
        return {"status": f"Manual scan triggered for group '{group}'."}
    else: # Automatic scan from cron-job.org
        print("--- Starting automatic scan cycle based on settings ---")
        try:
            g = Github(GITHUB_TOKEN); repo = g.get_repo(REPO_NAME)
            settings_content = repo.get_contents("settings.json").decoded_content.decode()
            settings = json.loads(settings_content)
            groups_to_scan = settings.get("auto_scan_groups", [])
            print(f"Found auto-scan groups: {groups_to_scan}")
            for g in groups_to_scan:
                await run_scan(g)
            return {"status": "Automatic scan finished."}
        except Exception as e:
            print(f"Could not run automatic scan: {e}")
            return {"error": "Could not read settings.json or run scan."}
