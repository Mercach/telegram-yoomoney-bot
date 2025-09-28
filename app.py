import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== Переменные окружения =====
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET")
RAILWAY_URL = os.getenv("RAILWAY_URL")  # например https://mybot.up.railway.app

if not BOT_TOKEN or not YOOMONEY_WALLET or not RAILWAY_URL:
    raise ValueError("Не заданы TELEGRAM_BOT_TOKEN, YOOMONEY_WALLET или RAILWAY_URL")

# ===== Flask и Telegram Application =====
app = Flask(__name__)
bot = Bot(BOT_TOKEN)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# ===== Функция отправки доступа =====
async def send_access(user_id):
    try:
        await bot.send_message(user_id, "✅ Оплата получена! Доступ выдан.")
    except Exception as e:
        print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

# ===== Команда /buy =====
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    amount = 1  # сумма в рублях
    pay_url = (
        f"https://yoomoney.ru/quickpay/confirm.xml?"
        f"receiver={YOOMONEY_WALLET}&quickpay-form=shop&targets=Оплата+доступа"
        f"&paymentType=SB&sum={amount}&label={user_id}"
    )
    await update.message.reply_text(
        f"💳 Оплата: {pay_url}\n\nПосле подтверждения платежа бот автоматически пришлёт доступ ✅"
    )

application.add_handler(CommandHandler("buy", buy))

# ===== Webhook для Telegram =====
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update_json = request.get_json(force=True)
    asyncio.run(process_update(update_json))
    return "OK", 200

async def process_update(update_json):
    update = Update.de_json(update_json, bot)
    await application.update_queue.put(update)

# ===== Уведомления от ЮMoney =====
@app.route("/notify", methods=["POST"])
def notify():
    data = request.form
    label = data.get("label")  # это user_id
    status = data.get("status")  # success, fail и т.д.
    
    if status == "success" and label:
        try:
            user_id = int(label)
            asyncio.run(send_access(user_id))
        except Exception as e:
            print(f"Ошибка при обработке уведомления ЮMoney: {e}")
    return "OK", 200

# ===== Установка webhook при старте =====
async def setup_webhook():
    await bot.delete_webhook()
    await bot.set_webhook(url=f"{RAILWAY_URL}/webhook/{BOT_TOKEN}")
    print(f"Webhook установлен: {RAILWAY_URL}/webhook/{BOT_TOKEN}")

if __name__ == "__main__":
    # Сначала ставим webhook
    asyncio.run(setup_webhook())
    
    # Запуск Flask
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
