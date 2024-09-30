from pydantic import BaseModel, Field
from typing import Optional, List


# Модель для запроса на логин
class LoginRequest(BaseModel):
    id: int = Field(..., description="ID пользователя")
    username: str = Field(..., description="Username пользователя")
    ip_address: Optional[str] = Field(None, description="IP адрес пользователя")


# Модель для ответа на логин
class LoginResponseModel(BaseModel):
    username: str
    not_tokens: int
    bones: int
    is_admin: bool


# Модель для реферальной статистики
class ReferralStatsModel(BaseModel):
    referral_id: int
    referral_username: str
    brought_in_bonus: float


# Модель для реферальной статистики с суммарной информацией
class ReferralStatsResponseModel(BaseModel):
    total_brought_in: float
    referrals: List[ReferralStatsModel]


# Модель для ответа с основной информацией о пользователе
class UserInfoResponseModel(BaseModel):
    id: int
    username: str
    bones: int
    not_tokens: int


# Модель для истории ставок и бонусов
class UserStatsResponseModel(BaseModel):
    total_bet_bones: int
    total_bet_not: int
    total_won_bones: float
    total_won_not: float
    total_referral_bonus: float


# Модель для регистрации нового пользователя
class RegisterUserRequest(BaseModel):
    username: str
    user_id: int
    client_ip: Optional[str]
    referral_code: Optional[str]
