import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Переменные окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET")
RAILWAY_URL = os.getenv("RAILWAY_URL")  # домен проекта, например https://mybot.up.railway.app

if not BOT_TOKEN:
    raise ValueError("Не задан TELEGRAM_BOT_TOKEN")

bot = Bot(BOT_TOKEN)
app = Flask(__name__)

# Telegram Application
application = Application.builder().token(BOT_TOKEN).updater(None).build()

# Команда /buy
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    amount = 1
    pay_url = (
        f"https://yoomoney.ru/quickpay/confirm.xml?"
        f"receiver={YOOMONEY_WALLET}&quickpay-form=shop&targets=Оплата+доступа"
        f"&paymentType=SB&sum={amount}&label={user_id}"
    )
    await update.message.reply_text(
        f"💳 Перейди по ссылке для оплаты:\n{pay_url}\n\nПосле подтверждения ЮMoney я сразу пришлю доступ ✅"
    )

# Регистрируем команду
application.add_handler(CommandHandler("buy", buy))

# Webhook endpoint (Telegram будет присылать апдейты сюда)
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# Проверка сервера
@app.route("/", methods=["GET"])
def home():
    return "Бот работает ✅", 200

# Асинхронная установка webhook
async def setup_webhook():
    await bot.delete_webhook()
    await bot.set_webhook(url=f"{RAILWAY_URL}/webhook/{BOT_TOKEN}")
    print(f"Webhook установлен: {RAILWAY_URL}/webhook/{BOT_TOKEN}")

def main():
    # Устанавливаем webhook
    asyncio.run(setup_webhook())

    # Запуск Flask
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
