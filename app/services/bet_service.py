from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.bet import Bet


class BetService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bet(self, user_id: int, card_id: int, amount: int, bet_type: str, round_id: int = None,
                         is_referral_bet: bool = False):
        new_bet = Bet(
            user_id=user_id,
            card_id=card_id,
            amount=amount,
            bet_type=bet_type,
            round_id=round_id,
            is_referral_bet=is_referral_bet
        )
        self.session.add(new_bet)
        await self.session.commit()
        return new_bet

    async def get_bet_by_id(self, bet_id: int):
        result = await self.session.execute(select(Bet).filter_by(id=bet_id))
        return result.scalars().first()

    async def get_bets_by_user_id(self, user_id: int):
        result = await self.session.execute(select(Bet).filter_by(user_id=user_id))
        return result.scalars().all()

    async def update_bet(self, bet_id: int, amount: int = None, bet_type: str = None, is_referral_bet: bool = None):
        bet = await self.get_bet_by_id(bet_id)
        if bet:
            if amount is not None:
                bet.amount = amount
            if bet_type is not None:
                bet.bet_type = bet_type
            if is_referral_bet is not None:
                bet.is_referral_bet = is_referral_bet
            await self.session.commit()
        return bet

    async def delete_bet(self, bet_id: int):
        bet = await self.get_bet_by_id(bet_id)
        if bet:
            await self.session.delete(bet)
            await self.session.commit()
