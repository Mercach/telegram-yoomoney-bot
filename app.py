import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# === Переменные окружения ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET")
RAILWAY_URL = os.getenv("RAILWAY_URL")  # например https://mybot.up.railway.app

if not BOT_TOKEN or not YOOMONEY_WALLET or not RAILWAY_URL:
    raise ValueError("Не заданы TELEGRAM_BOT_TOKEN, YOOMONEY_WALLET или RAILWAY_URL")

bot = Bot(BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).updater(None).build()
app = Flask(__name__)

# === /buy команда ===
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    amount = 1
    pay_url = (
        f"https://yoomoney.ru/quickpay/confirm.xml?"
        f"receiver={YOOMONEY_WALLET}&quickpay-form=shop&targets=Оплата+доступа"
        f"&paymentType=SB&sum={amount}&label={user_id}"
    )
    await update.message.reply_text(
        f"💳 Оплата: {pay_url}\n\nПосле подтверждения платежа бот автоматически пришлёт доступ ✅"
    )

application.add_handler(CommandHandler("buy", buy))

# === Webhook endpoint (Telegram присылает апдейты) ===
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# === ЮMoney /notify endpoint ===
@app.route("/notify", methods=["POST"])
def notify():
    data = request.form  # ЮMoney присылает данные формы
    label = data.get("label")  # это user_id, который мы передали в pay_url
    status = data.get("status")  # usually "success"
    
    if status == "success" and label:
        try:
            user_id = int(label)
            asyncio.run(send_access(user_id))
        except Exception as e:
            print(f"Ошибка при отправке доступа: {e}")
    return "OK", 200

# === Функция отправки доступа пользователю ===
async def send_access(user_id):
