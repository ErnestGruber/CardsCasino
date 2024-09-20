# Асинхронная функция для получения информации о ставке
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Bet


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
