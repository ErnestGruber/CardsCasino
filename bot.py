import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import Config
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id

    logging.info(f"Команда /start от {username} с ID {user_id}")

    web_app_url = f"https://uohvxb-194-35-116-160.ru.tuna.am"
    web_app_button = KeyboardButton(text="Открыть игру", web_app=WebAppInfo(url=web_app_url))
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(web_app_button)

    await message.answer("Нажмите кнопку ниже, чтобы открыть веб-приложение в Telegram:", reply_markup=keyboard)

# Запуск бота с логами и обработкой ошибок
async def start_bot():
    try:
        logging.info("Бот запущен!")
        await dp.start_polling()
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
        await bot.close()
        raise

if __name__ == '__main__':
    try:
        logging.info("Инициализация бота...")
        asyncio.run(start_bot())
    except Exception as e:
        logging.error(f"Основная ошибка: {e}")
