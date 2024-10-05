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
        # Обновляем статистику раунда в зависимости от типа ставки
        from app.services import RoundStatsService
        round_stats_service = RoundStatsService(self.session)

        if bet_type == "BONUS":
            # Увеличиваем только total_bones
            await round_stats_service.update_bank(round_id, bones_increase=amount)
        elif bet_type == "NOT":
            # Увеличиваем только total_not
            await round_stats_service.update_bank(round_id, not_increase=amount)

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

    async def has_user_bet_in_round(self, user_id: int, round_id: int):
        """
        Проверяет, делал ли пользователь ставку в данном раунде.
        Возвращает True, если есть хотя бы одна ставка, иначе False.
        """
        result = await self.session.execute(
            select(Bet).filter_by(user_id=user_id, round_id=round_id)
        )
        bet = result.scalars().first()
        return bet is not None