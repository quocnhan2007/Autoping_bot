import os
import time
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# Lấy token và URL từ biến môi trường
BOT_TOKEN = os.getenv("BOT_TOKEN")
PING_URL = os.getenv("PING_URL")
PING_INTERVAL = int(os.getenv("PING_INTERVAL", 300))  # mặc định 5 phút

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot đang hoạt động. Sẽ ping URL định kỳ.")

# Hàm ping URL
def ping_loop():
    while True:
        try:
            response = requests.get(PING_URL)
            logging.info(f"Ping {PING_URL} - Status: {response.status_code}")
        except Exception as e:
            logging.error(f"Lỗi khi ping: {e}")
        time.sleep(PING_INTERVAL)

# Khởi chạy bot
def main():
    from threading import Thread

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Chạy ping ở luồng riêng
    Thread(target=ping_loop, daemon=True).start()

    # Chạy bot Telegram
    app.run_polling()

if __name__ == "__main__":
    main()
