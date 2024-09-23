from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models import Card
from app.models.round import Round


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

    async def delete_round(self, round_id: int):
        round_obj = await self.get_round_by_id(round_id)
        if round_obj:
            await self.session.delete(round_obj)
            await self.session.commit()

    async def get_active_round(self):
        # Получаем активный раунд (где is_active=True)
        result = await self.session.execute(
            select(Round).filter_by(is_active=True)
        )
        active_round = result.scalars().first()

        return active_round