import os
import hmac
import hashlib
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET")
YOOMONEY_SECRET = os.getenv("YOOMONEY_SECRET")

if not BOT_TOKEN or not YOOMONEY_WALLET or not YOOMONEY_SECRET:
    raise ValueError("Не заданы переменные окружения: BOT_TOKEN, YOOMONEY_WALLET, YOOMONEY_SECRET")

bot = Bot(BOT_TOKEN)
app = Flask(__name__)

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

@app.route("/notify", methods=["POST"])
def notify():
    data = request.form.to_dict()
    string = "&".join([f"{k}={data[k]}" for k in sorted(data.keys()) if k != "sha1_hash"])
    signature = hmac.new(YOOMONEY_SECRET.encode(), string.encode(), hashlib.sha1).hexdigest()
    if signature == data.get("sha1_hash"):
        user_id = data.get("label")
        if user_id:
            bot.send_message(chat_id=user_id, text="✅ Оплата подтверждена! Вот твой доступ 🎉")
        return "OK"
    else:
        return "Invalid signature", 400

def start_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("buy", buy))
    application.run_polling()

def main():
    threading.Thread(target=start_bot, daemon=True).start()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
