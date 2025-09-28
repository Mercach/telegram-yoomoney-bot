from flask import Flask, request
from telegram import Bot, Update
from telegram.constants import ParseMode
import os
import requests

app = Flask(__name__)

# Берём токен из переменной окружения
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен!")

# Ссылка на webhook
RAILWAY_URL = os.environ.get("RAILWAY_URL")  # https://yourproject.up.railway.app
WEBHOOK_URL = f"{RAILWAY_URL}/webhook/{TELEGRAM_BOT_TOKEN}"

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Установка webhook при старте
def set_webhook():
    r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
                      data={"url": WEBHOOK_URL})
    if r.status_code == 200:
        print("Webhook установлен")
    else:
        print("Ошибка при установке webhook:", r.text)

set_webhook()

# Обработка webhook
@app.route(f"/webhook/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    if update.message and update.message.text:
        if update.message.text.lower() == "/buy":
            bot.send_message(
                chat_id=update.message.chat.id,
                text="Покупка принята ✅",
                parse_mode=ParseMode.MARKDOWN
            )
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
