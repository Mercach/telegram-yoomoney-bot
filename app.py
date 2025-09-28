from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import os
import asyncio

# Переменные окружения Railway
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET")
RAILWAY_URL = os.getenv("RAILWAY_URL")

app = Flask(__name__)
bot = Bot(TOKEN)

# --- Функция обработчик команды /buy ---
async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Отправляем простое сообщение пользователю
    await context.bot.send_message(chat_id=user_id,
                                   text=f"Привет! Чтобы оплатить, отправьте деньги на кошелек {YOOMONEY_WALLET}")
    # Здесь можно добавить логику проверки платежа и отправки доступа

# --- Telegram Application ---
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("buy", buy_command))

# --- Webhook endpoint ---
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.update_queue.put(update)
    return "OK"

# --- При запуске на Railway устанавливаем webhook ---
async def set_webhook():
    url = f"{RAILWAY_URL}/webhook/{TOKEN}"
    await bot.delete_webhook()
    await bot.set_webhook(url)
    print(f"Webhook установлен: {url}")

# --- Функция запуска приложения ---
def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    main()
