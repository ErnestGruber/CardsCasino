from pydantic import BaseModel
from typing import Optional, List


# Модель запроса на вывод средств
class CashoutRequestModel(BaseModel):
    wallet_address: str
    amount: int


# Модель для одной заявки на вывод средств
class CashoutResponseModel(BaseModel):
    id: int
    amount: int
    wallet_address: str
    is_processed: bool
    created_at: str
    processed_at: Optional[str]


# Модель для истории заявок на вывод средств
class CashoutHistoryResponseModel(BaseModel):
    cashout_requests: List[CashoutResponseModel]
