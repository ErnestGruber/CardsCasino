import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command  # Импортируем фильтр для команд

from api.user_api import generate_permanent_token
from models import User, db
from config import Config
import asyncio
import secrets
from app import app  # Импортируем Flask приложение для использования контекста

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()  # В Dispatcher ничего не передаем


# Проверка на приглашение через реферальную ссылку
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id

    args = message.get_args()  # Получаем аргументы, например, ?start=refwin

    with app.app_context():
        try:
            # Проверяем, существует ли пользователь
            user = User.query.filter_by(username=username).first()

            # Если пользователь не существует, регистрируем нового
            if not user:
                referral_code = secrets.token_hex(5)
                referred_by_user = None

                # Проверяем наличие аргументов для реферального кода
                if args and args.startswith("ref"):
                    referrer_code = args.split("=")[1]  # Получаем реферальный код
                    referred_by_user = User.query.filter_by(referral_code=referrer_code).first()

                    # Проверяем, что пользователь не может быть своим же рефералом
                    if referred_by_user and referred_by_user.username == username:
                        await message.reply("Вы не можете использовать свой собственный реферальный код!")
                        return

                # Генерируем постоянный токен и создаем нового пользователя
                permanent_token = generate_permanent_token()
                new_user = User(
                    id=user_id,
                    username=username,
                    bones=100,
                    not_tokens=10,
                    referral_code=referral_code,
                    referred_by=referred_by_user.referral_code if referred_by_user else None,
                    token=permanent_token  # Уникальный токен для постоянного доступа
                )
                db.session.add(new_user)
                db.session.commit()
                user = new_user

                # Если есть реферер, отправляем уведомление рефереру
                if referred_by_user:
                    logging.info(f"Новый пользователь {username} зарегистрировался через реферала {referred_by_user.username}.")
                    await message.bot.send_message(referred_by_user.id, f"Ваш реферал {username} зарегистрировался в системе!")

            # Генерируем ссылку с постоянным токеном для входа через веб-приложение
            web_app_url = f"https://yourdomain.com/login/{user.token}"  # Ссылка с постоянным токеном

            web_app_button = KeyboardButton(text="Открыть игру", web_app=WebAppInfo(url=web_app_url))
            keyboard = ReplyKeyboardMarkup(keyboard=[[web_app_button]], resize_keyboard=True)

            # Отправляем пользователю сообщение с кнопкой для входа
            await message.answer("Нажмите кнопку ниже, чтобы открыть веб-приложение в Telegram:", reply_markup=keyboard)

        except Exception as e:
            db.session.rollback()
            logging.error(f"Ошибка при добавлении пользователя: {e}")
            await message.reply("Произошла ошибка при регистрации. Попробуйте снова.")



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
