import logging
import secrets

from fastapi import APIRouter, Request, Depends, HTTPException, Header, Body, Response
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Bet, ReferralStats
from app.services import UserService, ReferralStatsService, RoundStatsService
from app.utils.users import get_token_from_header
from app.api.schemas.user import (LoginRequest, LoginResponseModel, ReferralStatsResponseModel, UserInfoResponseModel,
                          UserStatsResponseModel, RegisterUserRequest)  # Импортируем схемы
user_api = APIRouter()

# Секретный ключ для защиты регистраций
SECRET_KEY = "your_secret_key"

# POST запрос для логина
@user_api.post('/login', response_model=LoginResponseModel)
async def api_login(
        login_data: LoginRequest,
        response: Response,
        db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)

    user = await user_service.get_user_by_id(login_data.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.username != login_data.username:
        user.username = login_data.username
        await db.commit()

    if login_data.ip_address:
        await user_service.update_user_ip(user.id, login_data.ip_address)
        await db.commit()

    token = await user_service.get_user_token(user.id)
    response.set_cookie(key="token", value=token, httponly=True)

    return {
        'username': user.username,
        'not_tokens': user.not_tokens,
        'bones': user.bones,
        'is_admin': user.is_admin
    }


# Получение реферальной статистики
@user_api.get('/referrals', response_model=ReferralStatsResponseModel)
async def get_referral_stats(
    db: AsyncSession = Depends(get_db),
    token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)
    referral_stats_service = ReferralStatsService(db)

    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    referrals = await user_service.get_users_referred_by(user.referral_code)
    referral_stats = []
    total_brought_in = 0

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


# Получение основной информации о пользователе
@user_api.get('/user-info', response_model=UserInfoResponseModel)
async def get_user_info(
    db: AsyncSession = Depends(get_db),
    token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)

    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": user.id, "username": user.username, "bones": user.bones, "not_tokens": user.not_tokens}


# Получение статистики пользователя
@user_api.get('/user-stats', response_model=UserStatsResponseModel)
async def get_user_stats(
        db: AsyncSession = Depends(get_db),
        token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)
    round_stats_service = RoundStatsService(db)

    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_bets = await db.execute(select(Bet).filter_by(user_id=user.id))
    user_bets = user_bets.scalars().all()

    total_bet_bones = sum(bet.amount for bet in user_bets if bet.bet_type == "BONES")
    total_bet_not = sum(bet.amount for bet in user_bets if bet.bet_type == "NOT")

    total_won_bones = 0
    total_won_not = 0

    for bet in user_bets:
        round_stats = await round_stats_service.get_round_stats_by_round_id(bet.round_id)
        if round_stats and bet.card_id == round_stats.winner_card_id:
            total_won_bones += round_stats.bones_coefficient * bet.amount
            total_won_not += round_stats.not_coefficient * bet.amount

    referral_bonuses = await db.execute(select(ReferralStats).filter_by(referrer_id=user.id))
    referral_bonuses = referral_bonuses.scalars().all()

    total_referral_wins = sum(bonus.referrer_bonus for bonus in referral_bonuses)

    return {
        'total_bet_bones': total_bet_bones,
        'total_bet_not': total_bet_not,
        'total_won_bones': total_won_bones,
        'total_won_not': total_won_not,
        'total_referral_bonus': total_referral_wins
    }


# Регистрация пользователя
@user_api.post('/register-user', response_model=LoginResponseModel)
async def register_user(
    request_data: RegisterUserRequest,
    db: AsyncSession = Depends(get_db),
    secret_key: str = Header(None, alias="Secret-Key")
):
    if secret_key != "HAHAHA":
        raise HTTPException(status_code=403, detail="Invalid secret key")

    user_service = UserService(db)

    existing_user = await user_service.get_user_by_id(request_data.user_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    referred_by_user = None
    if request_data.referral_code:
        referred_by_user = await user_service.get_user_by_referral_code(request_data.referral_code)
        if not referred_by_user:
            raise HTTPException(status_code=404, detail="Referrer not found")

    permanent_token = await generate_permanent_token(user_service)
    new_referral_code = await generate_referral_code(user_service)

    new_user = await user_service.create_user(
        id=request_data.user_id,
        username=request_data.username,
        bones=100,
        not_tokens=100,
        referral_code=new_referral_code,
        referred_by=referred_by_user.referral_code if referred_by_user else None,
        token=permanent_token,
    )

    return {"message": "User successfully registered", "user_id": new_user.id, "token": permanent_token}


# Генерация уникального реферального кода
async def generate_referral_code(user_service: UserService) -> str:
    new_referral_code = secrets.token_hex(8)  # Генерируем реферальный код
    while await user_service.check_referral_code_exists(new_referral_code):
        new_referral_code = secrets.token_hex(8)  # Повторная генерация при совпадении
    return new_referral_code

# Генерация уникального токена для пользователя
async def generate_permanent_token(user_service: UserService) -> str:
    new_token = secrets.token_urlsafe(16)  # Генерируем токен
    while await user_service.check_token_exists(new_token):  # Проверка на уникальность
        new_token = secrets.token_urlsafe(16)  # Повторная генерация при совпадении
    return new_token
