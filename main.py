# main.py (เวอร์ชันสำหรับ Cron Job)
import os
import yfinance as yf
import pandas_ta as ta
import telegram
import asyncio

# --- การตั้งค่าเริ่มต้น ---
# รายชื่อสินทรัพย์ที่คุณต้องการสแกน (สามารถเพิ่ม/ลดได้ตามต้องการ)
# ใช้ Ticker จาก Yahoo Finance: https://finance.yahoo.com/
TICKERS_TO_SCAN = [
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", # Crypto
    "SPY", "QQQ", "VOO", # S&P500 / Nasdaq100 ETFs
    "AAPL", "MSFT", "GOOGL", "TSLA", "NVDA" # หุ้นรายตัว
]

# ตั้งค่า Indicator
VOLUME_MULTIPLIER = 2.0  # Volume ต้องมากกว่าค่าเฉลี่ย 2 เท่า
TIME_FRAME = "1d"      # Timeframe ที่จะวิเคราะห์: 1d=Daily, 4h=4 Hours, 1h=1 Hour

# --- ดึงข้อมูลลับจาก Environment Variables ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- ฟังก์ชันหลัก ---

async def send_telegram_message(message: str):
    """ฟังก์ชันสำหรับส่งข้อความไปที่ Telegram"""
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
    """วิเคราะห์สินทรัพย์รายตัวเพื่อหาสัญญาณ"""
    print(f"--- กำลังวิเคราะห์ {ticker} ---")
    try:
        # 1. ดึงข้อมูลด้วย yfinance
        # หมายเหตุ: สำหรับ Timeframe 4h และ 1h อาจต้องใช้ period ที่สั้นลง เช่น "60d"
        data = yf.download(ticker, period="200d", interval=TIME_FRAME, progress=False)
        if data.empty:
            print(f"ไม่พบข้อมูลสำหรับ {ticker}")
            return

        # 2. คำนวณ Indicators ด้วย pandas_ta
        data.ta.ema(length=100, append=True, col_names=('EMA100'))
        data.ta.ema(length=200, append=True, col_names=('EMA200'))
        data.ta.rsi(length=14, append=True, col_names=('RSI_14'))
        data.ta.macd(fast=12, slow=26, signal=9, append=True, col_names=('MACD', 'MACDh', 'MACDs'))
        data.ta.sma(length=20, close='Volume', append=True, col_names=('Volume_SMA20'))

        # 3. ดึงข้อมูลจาก "แท่งเทียนล่าสุด" มาตรวจสอบ
        latest = data.iloc[-1]
        
        # --- ตรวจสอบเงื่อนไขสัญญาณ ---
        
        # สัญญาณ Volume Spike
        is_volume_spike = latest['Volume'] > (latest['Volume_SMA20'] * VOLUME_MULTIPLIER)
        if is_volume_spike:
            message = (
                f"🔔 *Volume Spike Alert!*\n\n"
                f"*{ticker}* ({TIME_FRAME})\n"
                f"Volume ปัจจุบันพุ่งสูงกว่าค่าเฉลี่ย!"
            )
            await send_telegram_message(message)

        # สัญญาณ Bullish (เงื่อนไข Buy)
        is_above_emas = latest['Close'] > latest['EMA100'] and latest['Close'] > latest['EMA200']
        is_rsi_strong = latest['RSI_14'] > 55 # เพิ่มเงื่อนไขให้เข้มขึ้นเล็กน้อย
        is_macd_positive = latest['MACD'] > latest['MACDs']
        
        if is_above_emas and is_rsi_strong and is_macd_positive and is_volume_spike:
            message = (
                f"🚀 *Strong Buy Signal!*\n\n"
                f"*{ticker}* ({TIME_FRAME})\n"
                f"ราคา: {latest['Close']:.2f}\n"
                f"เงื่อนไข: ยืนเหนือ EMA, RSI > 55, MACD ตัดขึ้น, Volume Spike"
            )
            await send_telegram_message(message)

    except Exception as e:
        print(f"เกิดข้อผิดพลาดระหว่างวิเคราะห์ {ticker}: {e}")

async def main():
    """ฟังก์ชันหลักที่จะถูกรันโดย Cron Job"""
    print("--- เริ่มการสแกนรอบใหม่ ---")
    for ticker in TICKERS_TO_SCAN:
        await analyze_ticker(ticker)
    print("--- การสแกนเสร็จสิ้น ---")

if __name__ == "__main__":
    asyncio.run(main())
