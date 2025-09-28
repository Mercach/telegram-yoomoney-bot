import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Переменные окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET")
RAILWAY_URL = os.getenv("RAILWAY_URL")  # домен проекта, например https://mybot.up.railway.app

if not BOT_TOKEN or not YOOMONEY_WALLET or not RAILWAY_URL:
    raise ValueError("Не заданы TELEGRAM_BOT_TOKEN, YOOMONEY_WALLET или RAILWAY_URL")

# Создаём приложение
application = Application.builder().token(BOT_TOKEN).build()


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


# Запуск webhook (Telegram будет слать апдейты сюда)
def main():
    port = int(os.getenv("PORT", 5000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=f"{RAILWAY_URL}/webhook/{BOT_TOKEN}"
    )
    print(f"Webhook установлен: {RAILWAY_URL}/webhook/{BOT_TOKEN}")


if __name__ == "__main__":
    main()
