import logging
import secrets

from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel, Field

from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import UserService, ReferralStatsService
from app.utils.users import register_user, get_ip, get_token_from_header

user_api = APIRouter()

class LoginRequest(BaseModel):
    id: int = Field(..., description="ID пользователя")
    token: str = Field(..., description="Токен пользователя")
    referral_code: str = Field(None, description="Реферальный код")  #

# POST запрос для логина
@user_api.post('/api/login')
async def api_login(
        login_data: LoginRequest,
        db: AsyncSession = Depends(get_db)
):
    logging.info("Запрос получен", login_data)

    user_service = UserService(db)

    # Проверяем наличие пользователя по токену
    user = await user_service.get_user_by_token(login_data.token)

    if not user or user.id != login_data.id:
        raise HTTPException(status_code=404, detail="User not found or incorrect ID")

    # Если передан реферальный код, обрабатываем его
    if login_data.referral_code and not user.referred_by:
        referrer = await user_service.get_user_by_referral_code(login_data.referral_code)
        if referrer and referrer.id != user.id:
            user.referred_by = referrer.referral_code
            await db.commit()

    return {
        'username': user.username,
        'not_tokens': user.not_tokens,
        'bones': user.bones,
        'is_admin': user.is_admin
    }

# Получение реферальной статистики
@user_api.get('/api/referrals')
async def get_referral_stats(
    db: AsyncSession = Depends(get_db),
    token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)
    referral_stats_service = ReferralStatsService(db)

    # Получаем пользователя по токену
    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем рефералов пользователя
    referrals = await user_service.get_users_referred_by(user.referral_code)
    referral_stats = []
    total_brought_in = 0

    # Для каждого реферала собираем данные о реферальных бонусах
    for referral in referrals:
        stats = await referral_stats_service.get_stats_by_referrer(user.id)
        total_for_referral = sum(stat.referrer_bonus for stat in stats)
        total_brought_in += total_for_referral

        referral_stats.append({
            'referral_id': referral.id,
            'referral_username': referral.username,
            'brought_in_bonus': total_for_referral
        })

    return {
        'total_brought_in': total_brought_in,
        'referrals': referral_stats
    }

def generate_referral_code():
    return secrets.token_hex(5)
# Создаем уникальный токен для пользователя при регистрации
def generate_permanent_token():
    return secrets.token_urlsafe(16)
def generate_referral_link(user):
    referral_code = user.referral_code
    referral_link = f"https://t.me/YourTelegramBot?start={referral_code}"
    return referral_link