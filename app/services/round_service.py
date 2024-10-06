from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models import Card
from app.models.round import Round
from app.services import RoundStatsService


class RoundService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_round(self, description: str, target: str, start_time: datetime, end_time: datetime,
                           card_urls: list[str], is_active: bool = False):
        # Создаем новый раунд
        new_round = Round(
            description=description,
            target=target,
            start_time=start_time,
            end_time=end_time,
            is_active=is_active
        )
        self.session.add(new_round)
        await self.session.commit()

        # Добавляем карты, связанные с раундом
        cards = [Card(image_url=url, round_id=new_round.id) for url in card_urls]
        self.session.add_all(cards)
        await self.session.commit()
        # Добавляем статистику:
        # Создаем статистику раунда с начальными значениями
        round_stats_service = RoundStatsService(self.session)

        # Создание статистики раунда с начальными значениями
        await round_stats_service.create_round_stats(
            round_id=new_round.id,
            total_bones=0.0,  # Начальное значение
            total_not=0.0,  # Начальное значение
            total_bank=0.0,  # Начальное значение
            admin_fee=0.0,  # Комиссия администратора (примерное значение, можно изменить)
            bones_coefficient=0.0,  # Начальное значение
            not_coefficient=0.0,  # Начальное значение
        )
        return new_round

    async def get_round_by_id(self, round_id: int):
        result = await self.session.execute(select(Round).filter_by(id=round_id))
        return result.scalars().first()

    async def get_active_rounds(self):
        result = await self.session.execute(select(Round).filter_by(is_active=True))
        return result.scalars().all()

    async def update_round(self, round_id: int, description: str = None, target: str = None,
                           start_time: datetime = None, end_time: datetime = None, is_active: bool = None):
        round_obj = await self.get_round_by_id(round_id)
        if round_obj:
            if description is not None:
                round_obj.description = description
            if target is not None:
                round_obj.target = target
            if start_time is not None:
                round_obj.start_time = start_time
            if end_time is not None:
                round_obj.end_time = end_time
            if is_active is not None:
                round_obj.is_active = is_active
            await self.session.commit()
        return round_obj

    # Метод для завершения активного раунда
    async def end_round(self, round_id: int):
        active_round = await self.get_round_by_id(round_id)
        if active_round and active_round.is_active:
            active_round.is_active = False
            active_round.end_time = datetime.utcnow()  # Устанавливаем время окончания
            await self.session.commit()
        return active_round

    async def get_active_round(self):
        # Получаем активный раунд (где is_active=True)
        result = await self.session.execute(
            select(Round).filter_by(is_active=True)
        )
        active_round = result.scalars().first()

        return active_round

    async def get_latest_round(self):
        # Получаем последний раунд по ID
        result = await self.session.execute(
            select(Round).order_by(Round.id.desc()).limit(1)
        )
        latest_round = result.scalars().first()

        return latest_round