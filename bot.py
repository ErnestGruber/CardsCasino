import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from models import User, db
from config import Config
from sqlalchemy.exc import IntegrityError
import asyncio
from app import app  # Импортируем Flask приложение для использования контекста

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

    # Используем контекст приложения для работы с базой данных
    with app.app_context():
        try:
            # Проверяем, есть ли пользователь в базе данных по username
            user = User.query.filter_by(username=username).first()

            if user:
                logging.info(f"Пользователь {username} уже существует.")
                await message.reply(f"Привет, {username}! Добро пожаловать обратно в игру!")
            else:
                # Добавляем нового пользователя в базу данных
                logging.info(f"Добавляем пользователя {username} в базу данных.")
                new_user = User(id=user_id, username=username, bones=100, not_tokens=10)
                db.session.add(new_user)
                db.session.commit()  # Сохраняем изменения в базе данных
                logging.info(f"Пользователь {username} успешно добавлен.")
                await message.reply(f"Привет, {username}! Ты зарегистрирован в системе!")
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"Ошибка при добавлении пользователя: {e}")
            await message.reply(f"Произошла ошибка при регистрации. Попробуй снова.")
        except Exception as e:
            logging.error(f"Произошла непредвиденная ошибка: {e}")
            await message.reply(f"Ошибка на сервере. Попробуйте позже.")

    # Используем HTTPS URL с ngrok или внешним сервером
    web_app_url = f"https://xlj135-194-35-116-160.ru.tuna.am/login/{user_id}"

    # Создаем кнопку с WebApp
    web_app_button = KeyboardButton(text="Открыть игру", web_app=WebAppInfo(url=web_app_url))
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(web_app_button)

    await message.answer("Нажмите кнопку ниже, чтобы открыть веб-приложение в Telegram:", reply_markup=keyboard)

# Запуск бота с логами и обработкой ошибок
async def start_bot():
    logging.info("Запуск бота...")
    try:
        await dp.start_polling()
    except Exception as e:
        logging.error(f"Ошибка при запуске polling: {e}")
        await bot.close()
        raise

# Запуск программы
if __name__ == '__main__':
    try:
        logging.info("Инициализация бота...")
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот завершает работу...")
    except Exception as e:
        logging.error(f"Основная ошибка: {e}")
