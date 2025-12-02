
import os

import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальный словарь для хранения состояния пользователей
user_state = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = {"step": 1}
    
    message = (
        "В ответ на данное сообщение введите протяжённость всего маршрута. "
        "Заранее от МКАД рассчитайте по Яндекс Картам расстояние маршруту в одну сторону. "
        "Необходимо проставить ВСЕ точки, чтобы правильно определить общий пробег."
    )
    await update.message.reply_text(message)

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in user_state:
        await update.message.reply_text("Пожалуйста, начните с команды /start")
        return
    
    step = user_state[user_id]["step"]
    
    if step == 1:
        # Получаем расстояние (ожидаем число) и сохраняем в km
        try:
            km = float(text.replace(",", "."))
            user_state[user_id]["km"] = km
            user_state[user_id]["step"] = 2
            
            # Создаём клавиатуру с кнопками «Да» и «Нет»
            reply_keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    ["Да"],
                    ["Нет"]
                ],
                resize_keyboard=True,
                one_time_keyboard=True  # клавиатура скрывается после выбора
            )
            
            message = (
                "В заказе только мебель Vigo? "
                "Если заказ состоит из мебели Vigo более чем на половину — нажмите «Да». "
                "Если нет — нажмите «Нет»."
            )
            await update.message.reply_text(
                message,
                reply_markup=reply_keyboard
            )
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите число (расстояние в км).")
    
    elif step == 2:
        # Обрабатываем выбор с кнопок
        if text == "Да":
            marg = 15
        elif text == "Нет":
            marg = 17
        else:
            # Если пользователь ввёл текст вместо нажатия кнопки
            await update.message.reply_text(
                "Пожалуйста, используйте кнопки «Да» или «Нет».",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[["Да"], ["Нет"]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
            )
            return
        
        # Остальные параметры
        realPrib = 10
        rash = 82
        km = user_state[user_id]["km"]
        
        # Расчёты
        minZagruz = rash * km / marg * 100
        otlZagruz = rash * km / (marg - realPrib) * 100
        sredZahruz = (minZagruz + otlZagruz) / 2
        
        # Округляем до 2 знаков после запятой
        minZagruz = round(minZagruz, 2)
        sredZahruz = round(sredZahruz, 2)
        otlZagruz = round(otlZagruz, 2)
        
        # Отправляем результат
        result = (
            f"Минимальная сумма поездки = {minZagruz} руб.\n"
            f"Допустимая сумма поездки = {sredZahruz} руб.\n"
            f"Отличная сумма для поездки = {otlZagruz} руб."
        )
        await update.message.reply_text(result)
        
        # Сбрасываем состояние пользователя
        user_state.pop(user_id)

# Основной блок
def main():
    # Ваш токен от BotFather
    # TOKEN = os.getenv("TELEGRAM_TOKEN")
    TOKEN = "8025787203:AAHtQhoGoEtYTPw7CpWspPPIEAAScsTsk7A"
    
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
