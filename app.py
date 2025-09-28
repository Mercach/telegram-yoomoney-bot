import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

# Получаем токен и вебхук из переменных окружения
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Например: https://your-project.up.railway.app/webhook

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Диспетчер команд
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# Команда /buy
def buy(update, context):
    update.message.reply_text("Оплата принята! ✅")

dispatcher.add_handler(CommandHandler("buy", buy))

# Роут для вебхука
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# Установка вебхука при первом запуске
@app.before_first_request
def set_webhook():
    bot.set_webhook(WEBHOOK_URL + f"/{TOKEN}")
    print("Webhook установлен:", WEBHOOK_URL + f"/{TOKEN}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
