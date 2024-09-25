from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.awards import Awards


class AwardsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_award_for_user(self, user_id: int):
        # Создание наград для пользователя
        new_awards = Awards(user_id=user_id)
        self.session.add(new_awards)
        await self.session.commit()
        return new_awards

    async def get_awards_by_user_id(self, user_id: int):
        result = await self.session.execute(select(Awards).filter_by(user_id=user_id))
        return result.scalars().first()

    async def update_awards(self, user_id: int, **rules):
        awards = await self.get_awards_by_user_id(user_id)
        if awards:
            for rule, value in rules.items():
                if hasattr(awards, rule):
                    setattr(awards, rule, value)
            await self.session.commit()
        return awards