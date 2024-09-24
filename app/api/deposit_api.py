import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services import UserService
from app.services.deposit_service import DepositService
from app.utils.users import get_token_from_header


# Модель для запроса на пополнение
class DepositRequestModel(BaseModel):
    wallet_address: str = Field(..., description="Wallet address of the user")
    amount: int = Field(..., gt=0, description="Amount to deposit")

    # Валидатор для проверки формата адреса кошелька
    @validator('wallet_address')
    def validate_wallet_address(cls, value):
        pattern = r'^[A-Za-z0-9-]{43,50}$'
        if not re.match(pattern, value):
            raise ValueError(
                'Invalid wallet address format. It should be between 43 and 50 characters long, and contain only alphanumeric characters and dashes.')
        return value

deposit_api = APIRouter()


# Метод на создание заявки на пополнение
@deposit_api.post('/create-deposit')
async def create_deposit(
        deposit_request: DepositRequestModel,
        db: AsyncSession = Depends(get_db),
        token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)
    deposit_service = DepositService(db)

    # Получаем пользователя по токену
    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, есть ли необработанная заявка на пополнение
    existing_request = await deposit_service.get_pending_deposit_request_user(user.id)
    if existing_request:
        raise HTTPException(status_code=400, detail="A pending deposit request already exists.")

    # Создание новой заявки на пополнение
    deposit_request_obj = await deposit_service.create_deposit_request(
        user_id=user.id,
        wallet_address=deposit_request.wallet_address,
        amount=deposit_request.amount
    )

    return {"message": "Deposit request created", "request_id": deposit_request_obj.id}


# Метод на получение всех заявок на пополнение (и обработанных, и нет)
@deposit_api.get('/deposits')
async def get_deposits(
        db: AsyncSession = Depends(get_db),
        token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)
    deposit_service = DepositService(db)

    # Получаем пользователя по токену
    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем необработанную заявку пользователя
    pending_deposit = await deposit_service.get_pending_deposit_request_user(user.id)

    # Получаем все обработанные заявки пользователя
    complete_deposits = await deposit_service.get_complete_deposit_requests_user(user.id)

    # Форматируем данные
    formatted_pending_deposit = None
    if pending_deposit:
        formatted_pending_deposit = {
            "is_processed": pending_deposit.is_processed,
            "processed_at": pending_deposit.processed_at,
            "amount": pending_deposit.amount,
            "created_at": pending_deposit.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        }

    formatted_complete_deposits = [
        {
            "is_processed": deposit.is_processed,
            "processed_at": deposit.processed_at.strftime('%Y-%m-%dT%H:%M:%S.%f')[
                            :-3] if deposit.processed_at else None,
            "amount": deposit.amount,
            "created_at": deposit.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        }
        for deposit in complete_deposits
    ]

    return {
        "pending_deposit": formatted_pending_deposit,
        "complete_deposits": formatted_complete_deposits
    }