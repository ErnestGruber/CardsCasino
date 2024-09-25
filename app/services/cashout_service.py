from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.cashout_request import CashoutRequest

class CashoutService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # Создание заявки на вывод средств
    async def create_cashout_request(self, user_id: int, wallet_address: str, amount: int):
        new_cashout = CashoutRequest(
            user_id=user_id,
            wallet_address=wallet_address,
            amount=amount
        )
        self.session.add(new_cashout)
        await self.session.commit()
        return new_cashout

    # Проверка наличия необработанной заявки на вывод
    async def get_pending_cashout_request_user(self, user_id: int):
        result = await self.session.execute(select(CashoutRequest).filter_by(user_id=user_id, is_processed=False))
        return result.scalars().first()

    # Получение всех завершённых заявок пользователя
    async def get_complete_cashout_requests_user(self, user_id: int):
        result = await self.session.execute(select(CashoutRequest).filter_by(user_id=user_id, is_processed=True))
        return result.scalars().all()

    # Получение всех заявок пользователя (для истории)
    async def get_all_cashout_requests_user(self, user_id: int):
        result = await self.session.execute(select(CashoutRequest).filter_by(user_id=user_id))
        return result.scalars().all()

    async def approve_cashout(self, cashout_id: int):
        # Получаем заявку по ID
        result = await self.session.execute(select(CashoutRequest).filter_by(id=cashout_id))
        cashout = result.scalars().first()

        if cashout and not cashout.is_processed:
            cashout.is_processed = True
            cashout.processed_at = datetime.utcnow()

            # Обновляем баланс пользователя
            user_result = await self.session.execute(select(User).filter_by(id=cashout.user_id))
            user = user_result.scalars().first()
            if user:
                user.not_tokens -= cashout.amount  # Вычитаем сумму с баланса пользователя
                if user.not_tokens < 0:  # Проверяем, что баланс не станет отрицательным
                    raise ValueError("Недостаточно средств на балансе пользователя для вывода")

            await self.session.commit()
            return True
        return False

    async def reject_cashout(self, cashout_id: int):
        # Получаем заявку по ID
        result = await self.session.execute(select(CashoutRequest).filter_by(id=cashout_id))
        cashout = result.scalars().first()

        if cashout and not cashout.is_processed:
            # Удаляем заявку
            await self.session.delete(cashout)
            await self.session.commit()
            return True
        return False

    async def get_pending_cashout_requests(self):
        # Получаем все необработанные заявки на вывод
        query = select(CashoutRequest).filter(CashoutRequest.is_processed == False)
        result = await self.session.execute(query)
        pending_cashouts = result.scalars().all()

        # Теперь для каждой заявки получаем соответствующего пользователя
        cashouts_with_users = []
        for cashout in pending_cashouts:
            user_query = select(User).filter(User.id == cashout.user_id)
            user_result = await self.session.execute(user_query)
            user = user_result.scalars().first()

            cashouts_with_users.append((cashout, user.username if user else "Unknown"))

        return cashouts_with_users

    async def get_complete_cashout_requests(self):
        # Получаем завершенные заявки на вывод
        query = select(CashoutRequest).filter(CashoutRequest.is_processed == True)
        result = await self.session.execute(query)
        complete_cashouts = result.scalars().all()

        # Получаем соответствующих пользователей
        cashouts_with_users = []
        for cashout in complete_cashouts:
            user_query = select(User).filter(User.id == cashout.user_id)
            user_result = await self.session.execute(user_query)
            user = user_result.scalars().first()

            cashouts_with_users.append((cashout, user.username if user else "Unknown"))

        return cashouts_with_users