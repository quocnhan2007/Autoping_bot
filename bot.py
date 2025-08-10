import os
import time
import requests
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from threading import Thread

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# Lấy token từ biến môi trường
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Cấu hình người dùng: user_id -> {"urls": {url: {"interval": int, "history": []}}}
user_configs = {}

# Hàm ping từng URL
def ping_worker(user_id, url, context):
    config = user_configs[user_id]["urls"][url]
    interval = config["interval"]

    while url in user_configs[user_id]["urls"]:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            latency = round(time.time() - start_time, 2)
            status = response.status_code
            result = {
                "time": time.strftime("%H:%M:%S"),
                "status": status,
                "latency": latency
}
            config["history"].append(result)
            message = (
                f"✅ Ping thành công\n"
                f"URL: {url}\n"
                f"Status: {status}\n"
                f"Latency: {latency}s"
)
        except Exception as e:
            result = {
                "time": time.strftime("%H:%M:%S"),
                "status": "error",
                "latency": "N/A"
}
            config["history"].append(result)
            message = f"❌ Ping thất bại\nURL: {url}\nLỗi: {e}"

        context.bot.send_message(chat_id=user_id, text=message)
        time.sleep(interval)

# Khởi động luồng ping
def start_ping_thread(user_id, url, context):
    thread = Thread(target=ping_worker, args=(user_id, url, context), daemon=True)
    thread.start()

# /start – hướng dẫn
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Chào bạn! Các lệnh hỗ trợ:\n"
        "/add <url> <giây> – Thêm URL để ping\n"
        "/remove <url> – Xóa URL\n"
        "/list – Liệt kê URL đang ping\n"
        "/report – Xem báo cáo ping\n"
        "/start – Hiển thị hướng dẫn"
)

# /add – thêm URL
async def add_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if len(args)!= 2:
        await update.message.reply_text("❗ Cú pháp: /add <url> <giây>")
        return

    url, interval = args
    try:
        interval = int(interval)
        user_configs.setdefault(user_id, {"urls": {}})
        user_configs[user_id]["urls"][url] = {"interval": interval, "history": []}
        await update.message.reply_text(f"✅ Đã thêm URL: {url} ({interval}s)")
        start_ping_thread(user_id, url, context)
    except ValueError:
        await update.message.reply_text("❗ Thời gian phải là số nguyên.")

# /remove – xóa URL
async def remove_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if len(args)!= 1:
        await update.message.reply_text("❗ Cú pháp: /remove <url>")
        return

    url = args[0]
    if user_id in user_configs and url in user_configs[user_id]["urls"]:
        del user_configs[user_id]["urls"][url]
        await update.message.reply_text(f"🗑️ Đã xóa URL: {url}")
    else:
        await update.message.reply_text("❌ URL không tồn tại.")

# /list – liệt kê URL
async def list_urls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    urls = user_configs.get(user_id, {}).get("urls", {})
    if not urls:
        await update.message.reply_text("📭 Chưa có URL nào.")
        return

    msg = "📋 Danh sách URL đang ping:\n"
    for url, data in urls.items():
msg += f"- {url} ({data['interval']}s)\n"
    await update.message.reply_text(msg)

*/report – báo cáo ping*
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    urls = user_configs.get(user_id, {}).get("urls", {})
    if not urls:
        await update.message.reply_text("📭 Không có dữ liệu.")
        return

    msg = "📊 Báo cáo ping gần nhất:\n"
    for url, data in urls.items():
        history = data["history"][-5:]  # lấy 5 lần gần nhất
        msg += f"\n🔗 {url}:\n"
        for h in history:
            msg += f"  - {h['time']}: {h['status']} ({h['latency']}s)\n"
    await update.message.reply_text(msg)

*Chạy bot*
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_url))
    app.add_handler(CommandHandler("remove", remove_url))
    app.add_handler(CommandHandler("list", list_urls))
    app.add_handler(CommandHandler("report", report))

    app.run_polling()

if *name* == " *main* ":
    main()
