from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services import UserService, CashoutService
from app.services.deposit_service import DepositService
from app.utils.users import get_token_from_header


class CashoutRequestModel(BaseModel):
    wallet_address: str
    amount: int


cashout_api = APIRouter()


@cashout_api.post('/cashout')
async def request_cashout(
        cashout_request: CashoutRequestModel,
        db: AsyncSession = Depends(get_db),
        token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)
    cashout_service = CashoutService(db)

    # Получаем пользователя по токену
    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем наличие необработанной заявки на вывод
    pending_request = await cashout_service.get_pending_cashout_request_user(user.id)
    if pending_request:
        raise HTTPException(status_code=400, detail="Pending cashout request already exists.")

    # Проверяем, хватает ли средств для вывода
    if user.not_tokens < cashout_request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds for cashout.")

    # Создаем новую заявку на вывод средств
    new_cashout = await cashout_service.create_cashout_request(user.id, cashout_request.wallet_address,
                                                               cashout_request.amount)

    # Обновляем баланс пользователя
    await user_service.update_user_not_tokens(user.id, -cashout_request.amount)

    return {"message": "Cashout request created", "request_id": new_cashout.id}


@cashout_api.get('/cashout/history')
async def get_cashout_history(
        db: AsyncSession = Depends(get_db),
        token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)
    cashout_service = CashoutService(db)

    # Получаем пользователя по токену
    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем историю заявок на вывод средств
    all_requests = await cashout_service.get_all_cashout_requests_user(user.id)

    # Форматирование данных
    formatted_requests = [
        {
            "id": request.id,
            "amount": request.amount,
            "wallet_address": request.wallet_address,
            "is_processed": request.is_processed,
            "created_at": request.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
            "processed_at": request.processed_at.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] if request.processed_at else None
        }
        for request in all_requests
    ]

    return {
        "cashout_requests": formatted_requests
    }
