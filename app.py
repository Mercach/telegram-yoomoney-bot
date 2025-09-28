import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Переменные окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET")
RAILWAY_URL = os.getenv("RAILWAY_URL")  # например https://mybot.up.railway.app

if not BOT_TOKEN or not YOOMONEY_WALLET or not RAILWAY_URL:
    raise ValueError("Не заданы TELEGRAM_BOT_TOKEN, YOOMONEY_WALLET или RAILWAY_URL")

bot = Bot(BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).updater(None).build()
app = Flask(__name__)

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

application.add_handler(CommandHandler("buy", buy))

# Webhook endpoint (Telegram присылает апдейты сюда)
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# Простая проверка
@app.route("/", methods=["GET"])
def home():
    return "Бот работает ✅", 200

# Установка webhook
@app.before_first_request
def setup_webhook():
    import asyncio
    async def inner():
        await bot.delete_webhook()
        await bot.set_webhook(url=f"{RAILWAY_URL}/webhook/{BOT_TOKEN}")
        print(f"Webhook установлен: {RAILWAY_URL}/webhook/{BOT_TOKEN}")
    asyncio.run(inner())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
