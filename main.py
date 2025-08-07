import os
from fastapi import FastAPI, Request
import telegram
import uvicorn

# --- โหลด Token และ Chat ID จาก Environment Variables บน Railway ---
# เราจะไปตั้งค่านี้บนเว็บ Railway กันทีหลัง ไม่ต้องใส่ในโค้ด
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ตรวจสอบว่า Token ถูกตั้งค่าหรือไม่
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("กรุณาตั้งค่า TELEGRAM_TOKEN และ TELEGRAM_CHAT_ID บน Railway")

bot = telegram.Bot(token=TELEGRAM_TOKEN)
app = FastAPI()

@app.get("/")
def read_root():
    return {"Status": "API is running!"}

@app.post("/webhook/tradingview")
async def tradingview_webhook(request: Request):
    """
    Endpoint สำหรับรับ Webhook จาก TradingView Alert
    """
    data = await request.body()
    message_from_tv = data.decode('utf-8')

    # สร้างข้อความที่จะส่งไป Telegram
    final_message = f"🔔 **TradingView Alert** 🔔\n\n{message_from_tv}"

    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode='Markdown')
        print(f"Sent to Telegram: {final_message}")
        return {"status": "ok"}
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return {"status": "error", "reason": str(e)}

# ส่วนนี้เพื่อให้ Railway รู้ว่าต้องรันแอปด้วย port อะไร
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
