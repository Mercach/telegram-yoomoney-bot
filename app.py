import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Телеграм токен
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # https://твоя-доменная-ссылка

app = Flask(__name__)
bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

# Обработчик команды /buy
async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ты написал /buy")

application.add_handler(CommandHandler("buy", buy_command))

# Webhook route
@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    update = Update.de_json(await request.get_json(), bot)
    await application.update_queue.put(update)
    return "OK"

# Ставим webhook при старте
@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    print(f"Webhook установлен: {WEBHOOK_URL + WEBHOOK_PATH}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(on_startup())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
