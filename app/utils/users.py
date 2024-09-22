# Асинхронная функция для получения информации о ставке
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Bet, User


async def getBet(round_id, user_id: int, session: AsyncSession):
    # Создаем запрос для поиска ставки пользователя на указанный раунд
    async with session.begin():
        result = await session.execute(
            select(Bet).filter_by(round_id=round_id, user_id=user_id)
        )
        bet = result.scalars().first()

    # Если ставка найдена, возвращаем ID раунда, иначе возвращаем False
    if bet:
        return bet.round_id
    else:
        return False

async def get_ip(request):
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr
    return client_ip

async def register_user(async_session, username, user_id, client_ip, referral_code=None):
    try:
        referred_by_user = None

        # Если передан реферальный код, ищем пользователя, который пригласил
        if referral_code:
            referred_by_user = await async_session.execute(select(User).filter_by(referral_code=referral_code))
            referred_by_user = referred_by_user.scalars().first()

        permanent_token = secrets.token_hex(16)  # Генерируем постоянный токен

        # Генерация уникального реферального кода
        new_referral_code = secrets.token_hex(10)
        while await async_session.execute(select(User).filter_by(referral_code=new_referral_code)).scalars().first():
            new_referral_code = secrets.token_hex(10)  # Повторная генерация кода, если найдено совпадение

        new_user = User(
            id=user_id,
            username=username,
            bones=100,
            not_tokens=10,
            referral_code=new_referral_code,
            referred_by=referred_by_user.referral_code if referred_by_user else None,
            token=permanent_token,
            ip_address=client_ip  # Записываем IP-адрес пользователя
        )

        async_session.add(new_user)
        await async_session.commit()

        logging.info(f"Пользователь {username} успешно зарегистрирован.")
        return new_user

    except Exception as e:
        await async_session.rollback()
        logging.error(f"Ошибка при регистрации пользователя: {e}")
        return None
