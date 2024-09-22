from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.round_stats import RoundStats


class RoundStatsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_round_stats(self, round_id: int, total_bones: float, total_not: float, total_bank: float,
                                 admin_fee: float, bones_coefficient: float, not_coefficient: float,
                                 winner_card_id: int):
        new_round_stats = RoundStats(
            round_id=round_id,
            total_bones=total_bones,
            total_not=total_not,
            total_bank=total_bank,
            admin_fee=admin_fee,
            bones_coefficient=bones_coefficient,
            not_coefficient=not_coefficient,
            winner_card_id=winner_card_id
        )
        self.session.add(new_round_stats)
        await self.session.commit()
        return new_round_stats

    async def get_round_stats_by_id(self, stats_id: int):
        result = await self.session.execute(select(RoundStats).filter_by(id=stats_id))
        return result.scalars().first()

    async def get_round_stats_by_round_id(self, round_id: int):
        result = await self.session.execute(select(RoundStats).filter_by(round_id=round_id))
        return result.scalars().first()

    async def update_round_stats(self, stats_id: int, total_bones: float = None, total_not: float = None,
                                 total_bank: float = None, admin_fee: float = None,
                                 bones_coefficient: float = None, not_coefficient: float = None):
        round_stats = await self.get_round_stats_by_id(stats_id)
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
            await self.session.commit()
        return round_stats

    async def delete_round_stats(self, stats_id: int):
        round_stats = await self.get_round_stats_by_id(stats_id)
        if round_stats:
            await self.session.delete
