import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Создаем приложение (новый способ)
application = ApplicationBuilder().token(TOKEN).build()

# Команда /buy
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"Привет, {update.effective_user.first_name}! Вы выбрали покупку.")
    print(f"Пользователь {user_id} нажал /buy")

# Регистрируем команду
application.add_handler(CommandHandler("buy", buy))

# Вебхук
@app.route("/webhook/<token>", methods=["POST"])
def webhook(token):
    if token != TOKEN:
        return "Unauthorized", 403
    update = Update.de_json(request.get_json(force=True), bot)
    application.run_update(update)
    return "OK", 200

if __name__ == "__main__":
    print("Бот готов к работе")
    app.run(host="0.0.0.0", port=8080)
