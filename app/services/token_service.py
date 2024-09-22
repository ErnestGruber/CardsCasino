from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.models.token import Token


class TokenService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_token(self, user_id: int, token: str, expires_at: datetime):
        new_token = Token(user_id=user_id, token=token, expires_at=expires_at)
        self.session.add(new_token)
        await self.session.commit()
        return new_token

    async def get_token_by_id(self, token_id: int):
        result = await self.session.execute(select(Token).filter_by(id=token_id))
        return result.scalars().first()

    async def get_token_by_value(self, token_value: str):
        result = await self.session.execute(select(Token).filter_by(token=token_value))
        return result.scalars().first()

    async def is_token_valid(self, token_value: str):
        token = await self.get_token_by_value(token_value)
        if token:
            return token.is_valid()
        return False

    async def delete_token(self, token_id: int):
        token = await self.get_token_by_id(token_id)
        if token:
            await self.session.delete(token)
            await self.session.commit()

    async def delete_expired_tokens(self):
        result = await self.session.execute(select(Token))
        tokens = result.scalars().all()
        for token in tokens:
            if not token.is_valid():
                await self.session.delete(token)
        await self.session.commit()
