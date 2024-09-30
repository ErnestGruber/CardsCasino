from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services import UserService, CashoutService
from app.utils.users import get_token_from_header
from app.api.schemas.cashout import CashoutRequestModel, CashoutResponseModel, CashoutHistoryResponseModel  # Импортируем схемы

cashout_api = APIRouter()


# Запрос на вывод средств
@cashout_api.post('/cashout', response_model=CashoutResponseModel)
async def request_cashout(
        cashout_request: CashoutRequestModel,
        db: AsyncSession = Depends(get_db),
        token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)
    cashout_service = CashoutService(db)

    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    pending_request = await cashout_service.get_pending_cashout_request_user(user.id)
    if pending_request:
        raise HTTPException(status_code=400, detail="Pending cashout request already exists.")

    if user.not_tokens < cashout_request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds for cashout.")

    new_cashout = await cashout_service.create_cashout_request(user.id, cashout_request.wallet_address, cashout_request.amount)

    await user_service.update_user_not_tokens(user.id, -cashout_request.amount)

    return {
        "id": new_cashout.id,
        "amount": cashout_request.amount,
        "wallet_address": cashout_request.wallet_address,
        "is_processed": new_cashout.is_processed,
        "created_at": new_cashout.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
        "processed_at": new_cashout.processed_at.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] if new_cashout.processed_at else None
    }


# История заявок на вывод средств
@cashout_api.get('/cashout/history', response_model=CashoutHistoryResponseModel)
async def get_cashout_history(
        db: AsyncSession = Depends(get_db),
        token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)
    cashout_service = CashoutService(db)

    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    all_requests = await cashout_service.get_all_cashout_requests_user(user.id)

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
