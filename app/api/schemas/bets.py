from pydantic import BaseModel
from typing import Optional, List


# Модель для отображения информации о ставке пользователя
class BetUserModel(BaseModel):
    card_id: Optional[int]
    won_amount: float


# Модель для отображения информации о статистике раунда
class RoundStatsModel(BaseModel):
    card_1_id: Optional[int]
    card1procentile: Optional[float]
    card_2_id: Optional[int]
    card2procentile: Optional[float]
    card_3_id: Optional[int]
    card3procentile: Optional[float]


# Модель для отображения информации о раунде
class RoundDataModel(BaseModel):
    round_id: int
    bet_user: Optional[BetUserModel]
    winner_card_id: Optional[int]
    round_stats: Optional[RoundStatsModel]


# Модель для списка всех раундов
class RoundsDataResponseModel(BaseModel):
    rounds: List[RoundDataModel]