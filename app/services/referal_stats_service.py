from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.referal_stats import ReferralStats

class ReferralStatsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_referral_stats(self, referrer_id: int, referral_id: int, referral_bet_id: int,
                                    admin_bonus: int, referrer_bonus: int):
        new_stats = ReferralStats(
            referrer_id=referrer_id,
            referral_id=referral_id,
            referral_bet_id=referral_bet_id,
            admin_bonus=admin_bonus,
            referrer_bonus=referrer_bonus
        )
        self.session.add(new_stats)
        await self.session.commit()
        return new_stats

    async def get_referral_stats_by_id(self, stats_id: int):
        result = await self.session.execute(select(ReferralStats).filter_by(id=stats_id))
        return result.scalars().first()

    async def get_stats_by_referrer(self, referrer_id: int):
        result = await self.session.execute(select(ReferralStats).filter_by(referrer_id=referrer_id))
        return result.scalars().all()

    async def update_referral_stats(self, stats_id: int, admin_bonus: int = None, referrer_bonus: int = None):
        stats = await self.get_referral_stats_by_id(stats_id)
        if stats:
            if admin_bonus is not None:
                stats.admin_bonus = admin_bonus
            if referrer_bonus is not None:
                stats.referrer_bonus = referrer_bonus
            await self.session.commit()
        return stats

    async def delete_referral_stats(self, stats_id: int):
        stats = await self.get_referral_stats_by_id(stats_id)
        if stats:
            await self.session.delete(stats)
            await self.session.commit()
