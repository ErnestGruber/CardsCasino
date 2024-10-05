from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.round_stats import RoundStats


class RoundStatsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_round_stats(self, round_id: int, total_bones: float, total_not: float, total_bank: float,
                                 admin_fee: float, bones_coefficient: float, not_coefficient: float):
        new_round_stats = RoundStats(
            round_id=round_id,
            total_bones=total_bones,
            total_not=total_not,
            total_bank=total_bank,
            admin_fee=admin_fee,
            bones_coefficient=bones_coefficient,
            not_coefficient=not_coefficient
        )
        self.session.add(new_round_stats)
        await self.session.commit()
        return new_round_stats


    async def update_round_stats(self, round_id: int, total_bones: float = None, total_not: float = None,
                                 total_bank: float = None,
                                 admin_fee: float = None, bones_coefficient: float = None,
                                 not_coefficient: float = None,
                                 winner_card_id: int = None):
        # Ищем запись статистики для данного раунда
        round_stats = await self.get_round_stats_by_round_id(round_id)

        # Если запись найдена, обновляем значения
        if round_stats:
            if total_bones is not None:
                round_stats.total_bones = total_bones
            if total_not is not None:
                round_stats.total_not = total_not
            if total_bank is not None:
                round_stats.total_bank = total_bank
            if admin_fee is not None:
                round_stats.admin_fee = admin_fee
            if bones_coefficient is not None:
                round_stats.bones_coefficient = bones_coefficient
            if not_coefficient is not None:
                round_stats.not_coefficient = not_coefficient
            if winner_card_id is not None:
                round_stats.winner_card_id = winner_card_id

            # Сохраняем изменения
            await self.session.commit()

            return round_stats
        else:
            # Если запись не найдена, возвращаем None или кидаем исключение
            return None


    async def get_round_stats_by_id(self, stats_id: int):
        result = await self.session.execute(select(RoundStats).filter_by(id=stats_id))
        return result.scalars().first()

    async def get_round_stats_by_round_id(self, round_id: int):
        result = await self.session.execute(select(RoundStats).filter_by(round_id=round_id))
        return result.scalars().first()

    async def update_bank(self, round_id: int, bones_increase: float = 0, not_increase: float = 0):
        # Получаем текущую статистику раунда
        result = await self.session.execute(
            select(RoundStats).filter_by(round_id=round_id)
        )
        round_stats = result.scalars().first()

        if round_stats:
            # Увеличиваем поля total_bones и total_not на указанные значения
            round_stats.total_bones += bones_increase
            round_stats.total_not += not_increase

            # Неявно total_bank будет равен сумме total_bones и total_not
            round_stats.total_bank = bones_increase + not_increase

            # Сохраняем изменения в базе данных
            await self.session.commit()

        return round_stats
