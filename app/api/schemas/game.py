from pydantic import BaseModel
from typing import List


# Модель для отображения карты
class CardModel(BaseModel):
    id: int
    image_url: str


# Модель для отображения активного раунда
class RoundModel(BaseModel):
    id: int
    description: str
    target: int


# Модель для ответа с данными о раунде и картах
class GameResponseModel(BaseModel):
    round: RoundModel
    cards: List[CardModel]

class GameBank(BaseModel):
    total_bank: float


# Модель для запроса на ставку
class BetRequest(BaseModel):
    round_id: int
    bet_type: str
    bet_amount: int


# Модель для ответа при размещении ставки FixMe - убрать id на проде
class BetResponseModel(BaseModel):
    success: str
    bet_id: int