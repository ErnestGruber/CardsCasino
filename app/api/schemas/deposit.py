from pydantic import BaseModel
from typing import Optional, List


# Модель для успешного ответа на создание заявки на пополнение
class DepositResponseModel(BaseModel):
    message: str
    request_id: int


# Модель для одного депозита
class DepositModel(BaseModel):
    is_processed: bool
    processed_at: Optional[str]  # Время может быть None, если заявка еще не обработана
    amount: int
    created_at: str


# Модель для ответа с списком всех заявок на пополнение
class DepositsListResponseModel(BaseModel):
    pending_deposit: Optional[DepositModel]  # Ожидаемая заявка может отсутствовать
    complete_deposits: List[DepositModel]  #