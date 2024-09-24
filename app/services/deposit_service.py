from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.models import DepositRequest, User
from app.services import UserService


class DepositService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_deposit_request(self, user_id: int, wallet_address: str, amount: int):
        new_deposit = DepositRequest(
            user_id=user_id,
            wallet_address=wallet_address,
            amount=amount,
            is_processed=False
        )
        self.session.add(new_deposit)
        await self.session.commit()
        return new_deposit

    async def get_pending_deposit_request_user(self, user_id: int):
        result = await self.session.execute(select(DepositRequest).filter_by(user_id=user_id, is_processed=False))
        return result.scalars().first()

    async def get_all_deposit_requests_user(self):
        pending = await self.session.execute(select(DepositRequest).filter_by(is_processed=False))
        complete = await self.session.execute(select(DepositRequest).filter_by(is_processed=True))
        return {
            "pending": pending.scalars().all(),
            "complete": complete.scalars().all()
        }

    # Получение всех необработанных заявок
    async def get_pending_deposits(self, start_date=None, end_date=None):
        # Сначала получаем все заявки на пополнение без использования JOIN
        query = select(DepositRequest).filter(DepositRequest.is_processed == False)
        result = await self.session.execute(query)
        pending_deposits = result.scalars().all()

        # Теперь для каждой заявки получаем соответствующего пользователя
        deposits_with_users = []
        for deposit in pending_deposits:
            user_query = select(User).filter(User.id == deposit.user_id)
            user_result = await self.session.execute(user_query)
            user = user_result.scalars().first()

            deposits_with_users.append((deposit, user.username if user else "Unknown"))

        return deposits_with_users

    async def get_complete_deposits(self, start_date=None, end_date=None):
        # Получаем завершенные депозиты
        query = select(DepositRequest).filter(DepositRequest.is_processed == True)
        result = await self.session.execute(query)
        complete_deposits = result.scalars().all()

        # Получаем соответствующих пользователей
        deposits_with_users = []
        for deposit in complete_deposits:
            user_query = select(User).filter(User.id == deposit.user_id)
            user_result = await self.session.execute(user_query)
            user = user_result.scalars().first()

            deposits_with_users.append((deposit, user.username if user else "Unknown"))

        return deposits_with_users

    # Метод для одобрения заявки
    async def approve_deposit(self, deposit_id: int):
        result = await self.session.execute(select(DepositRequest).filter_by(id=deposit_id))
        deposit = result.scalars().first()
        user_service = UserService(self.session)
        if deposit and not deposit.is_processed:
            deposit.is_processed = True
            deposit.processed_at = datetime.utcnow()
            # Здесь добавляем логику начисления средств пользователю
            # Например:
            await user_service.update_user_not_tokens(deposit.user_id, deposit.amount)
            await self.session.commit()
            return True
        return False

    async def reject_deposit(self, deposit_id: int):
        deposit = await self.session.get(DepositRequest, deposit_id)
        if deposit:
            await self.session.delete(deposit)
            await self.session.commit()
            return True
        return False