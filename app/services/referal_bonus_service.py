from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.referral_bonus import ReferralBonus


class ReferralBonusService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_referral_bonus(self, user_id: int, referred_user_id: int, bonus_bones: int = 0):
        new_bonus = ReferralBonus(
            user_id=user_id,
            referred_user_id=referred_user_id,
            bonus_bones=bonus_bones
        )
        self.session.add(new_bonus)
        await self.session.commit()
        return new_bonus

    async def get_referral_bonus_by_id(self, bonus_id: int):
        result = await self.session.execute(select(ReferralBonus).filter_by(id=bonus_id))
        return result.scalars().first()

    async def get_referral_bonuses_for_user(self, user_id: int):
        result = await self.session.execute(select(ReferralBonus).filter_by(user_id=user_id))
        return result.scalars().all()

    async def update_referral_bonus(self, bonus_id: int, bonus_bones: int):
        referral_bonus = await self.get_referral_bonus_by_id(bonus_id)
        if referral_bonus:
            referral_bonus.bonus_bones = bonus_bones
            await self.session.commit()
        return referral_bonus

    async def delete_referral_bonus(self, bonus_id: int):
        referral_bonus = await self.get_referral_bonus_by_id(bonus_id)
        if referral_bonus:
            await self.session.delete(referral_bonus)
            await self.session.commit()
