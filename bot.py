import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command  # Импортируем фильтр для команд
from models import User, db
from config import Config
from sqlalchemy.exc import IntegrityError
import asyncio
import secrets
from app import app  # Импортируем Flask приложение для использования контекста
from models.token import Token

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()  # В Dispatcher ничего не передаем

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id

    logging.info(f"Команда /start от {username} с ID {user_id}")

    with app.app_context():
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                logging.info(f"Добавляем нового пользователя {username} в базу данных.")
                new_user = User(id=user_id, username=username, bones=100, not_tokens=10)
                db.session.add(new_user)
                db.session.commit()
                user = new_user

            # Генерация уникального токена
            token_value = secrets.token_urlsafe(16)
            expiration_time = datetime.utcnow() + timedelta(hours=1)

            # Создаем запись токена в базе данных
            token = Token(user_id=user.id, token=token_value, expires_at=expiration_time)
            db.session.add(token)
            db.session.commit()

            web_app_url = f"https://92ucii-194-35-116-160.ru.tuna.am/login/{token_value}"  # Передаем токен, а не user_id

            web_app_button = KeyboardButton(text="Открыть игру", web_app=WebAppInfo(url=web_app_url))
            keyboard = ReplyKeyboardMarkup(keyboard=[[web_app_button]], resize_keyboard=True)

            await message.answer("Нажмите кнопку ниже, чтобы открыть веб-приложение в Telegram:", reply_markup=keyboard)

        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"Ошибка при добавлении пользователя: {e}")
            await message.reply(f"Произошла ошибка при регистрации. Попробуй снова.")
        except Exception as e:
            logging.error(f"Произошла непредвиденная ошибка: {e}")
            await message.reply(f"Ошибка на сервере. Попробуйте позже.")


# Запуск бота с логами и обработкой ошибок
async def start_bot():
    logging.info("Запуск бота...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)  # Очищаем старые вебхуки, если они есть
        await dp.start_polling(bot)  # Здесь передаем объект бота
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
