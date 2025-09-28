import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # имя переменной окружения должно совпадать с тем, что в Railway
bot = Bot(token=TOKEN)

app = Flask(__name__)

# Telegram команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот готов к работе!")

# Создаем Application
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Webhook для Flask
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)  # отправляем апдейт в очередь Application
    return "OK"

if __name__ == "__main__":
    # Запуск Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
