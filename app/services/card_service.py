from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.card import Card


class CardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_card(self, image_url: str, round_id: int, total_bones: int = 0, total_not: int = 0,
                          total_bank: int = 0, is_winner: bool = False):
        new_card = Card(
            image_url=image_url,
            round_id=round_id,
            total_bones=total_bones,
            total_not=total_not,
            total_bank=total_bank,
            is_winner=is_winner
        )
        self.session.add(new_card)
        await self.session.commit()
        return new_card

    async def get_card_by_id(self, card_id: int):
        result = await self.session.execute(select(Card).filter_by(id=card_id))
        return result.scalars().first()

    async def get_cards_by_round_id(self, round_id: int):
        result = await self.session.execute(select(Card).filter_by(round_id=round_id))
        return result.scalars().all()

    async def update_card(self, card_id: int, total_bones: int = None, total_not: int = None,
                          total_bank: int = None, is_winner: bool = None):
        card = await self.get_card_by_id(card_id)
        if card:
            if total_bones is not None:
                card.total_bones = total_bones
            if total_not is not None:
                card.total_not = total_not
            if total_bank is not None:
                card.total_bank = total_bank
            if is_winner is not None:
                card.is_winner = is_winner
            await self.session.commit()
        return card

    async def delete_card(self, card_id: int):
        card = await self.get_card_by_id(card_id)
        if card:
            await self.session.delete(card)
            await self.session.commit()
