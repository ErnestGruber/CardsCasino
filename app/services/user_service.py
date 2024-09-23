from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, id: int, token: str, username: str, bones: int = 100, not_tokens: int = 0,
                          referral_code: str = None, referred_by: str = None,
                          is_admin: bool = False, wallet_address: str = "0xDefaultWallet"):
        new_user = User(
            id=id,
            username=username,
            bones=bones,
            not_tokens=not_tokens,
            referral_code=referral_code,
            referred_by=referred_by,
            is_admin=is_admin,
            wallet_address=wallet_address,
            token=token
        )
        self.session.add(new_user)
        await self.session.commit()
        return new_user

    async def get_user_by_id(self, user_id: int):
        result = await self.session.execute(select(User).filter_by(id=user_id))
        return result.scalars().first()

    async def get_user_by_username(self, username: str):
        result = await self.session.execute(select(User).filter_by(username=username))
        return result.scalars().first()

    # Получение пользователей, приглашенных по данному реферальному коду
    async def get_users_referred_by(self, referral_code: str):
        result = await self.session.execute(select(User).filter_by(referred_by=referral_code))
        return result.scalars().all()

    async def get_user_by_token(self, token: str):
        result = await self.session.execute(select(User).filter_by(token=token))
        return result.scalars().first()

    async def get_user_by_referral_code(self, referral_code: str):
        result = await self.session.execute(select(User).filter_by(referral_code=referral_code))
        return result.scalars().first()

    async def update_user_bones(self, user_id: int, amount: int):
        user = await self.get_user_by_id(user_id)
        if user:
            user.bones += amount
            await self.session.commit()
        return user

    async def update_user_not_tokens(self, user_id: int, amount: int):
        user = await self.get_user_by_id(user_id)
        if user:
            user.not_tokens += amount
            await self.session.commit()
        return user

    async def delete_user(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()

    async def check_referral_code_exists(self, referral_code: str) -> bool:
        """Проверяет, существует ли пользователь с данным реферальным кодом"""
        result = await self.session.execute(
            select(User).filter_by(referral_code=referral_code)
        )
        user = result.scalars().first()
        return user is not None

    async def check_token_exists(self, token: str) -> bool:
        """Проверяет, существует ли пользователь с данным токеном"""
        result = await self.session.execute(
            select(User).filter_by(token=token)
        )
        user = result.scalars().first()
        return user is not None