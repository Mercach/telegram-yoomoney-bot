import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

# Берем токен из переменных окружения
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)

app = Flask(__name__)

# Создаем диспетчер, он обработает команды
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# Команда /buy
def buy(update, context):
    user_id = update.effective_user.id
    update.message.reply_text(f"Привет, {update.effective_user.first_name}! Вы выбрали покупку.")
    # Тут можно добавить логику оплаты или выдачи доступа
    print(f"Пользователь {user_id} нажал /buy")

# Регистрируем команду
dispatcher.add_handler(CommandHandler("buy", buy))

# Вебхук
@app.route("/webhook/<token>", methods=["POST"])
def webhook(token):
    if token != TOKEN:
        return "Unauthorized", 403
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    print("Бот готов к работе")
    app.run(host="0.0.0.0", port=8080)
