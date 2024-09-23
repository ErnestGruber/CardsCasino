import logging
import secrets

from fastapi import APIRouter, Request, Depends, HTTPException, Header, Body
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Bet, User
from app.services import UserService, ReferralStatsService, RoundStatsService
from app.utils.users import register_user, get_ip, get_token_from_header

user_api = APIRouter()

# Секретный ключ для защиты регистраций
SECRET_KEY = "your_secret_key"

class LoginRequest(BaseModel):
    id: int = Field(..., description="ID пользователя")
    token: str = Field(..., description="Токен пользователя")
    referral_code: str = Field(None, description="Реферальный код")  #

# POST запрос для логина
@user_api.post('/login')
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
@user_api.get('/referrals')
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


@user_api.get('/user-info')
async def get_user_info(
    db: AsyncSession = Depends(get_db),
    token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)

    # Получаем пользователя по токену
    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Возвращаем основные данные пользователя
    user_data = {
        "id": user.id,
        "username": user.username,
        "bones": user.bones,
        "not_tokens": user.not_tokens
    }

    return {"user": user_data}

@user_api.get('/get-referral-link')
async def get_referral_link(
        db: AsyncSession = Depends(get_db),
        token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)

    # Получаем пользователя по токену
    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Генерируем реферальную ссылку
    referral_link = f"https://t.me/YourTelegramBot?start={user.referral_code}"

    return {"referral_link": referral_link}

@user_api.get('/user-stats')
async def get_user_stats(
        db: AsyncSession = Depends(get_db),
        token_value: str = Depends(get_token_from_header)
):
    user_service = UserService(db)
    round_stats_service = RoundStatsService(db)

    # Получаем пользователя по токену
    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем ставки пользователя
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

    # Выигрыши от рефералов
    total_referral_wins = 0
    referrals = await db.execute(select(User).filter_by(referred_by=user.referral_code))
    referrals = referrals.scalars().all()

    for referral in referrals:
        referral_bets = await db.execute(select(Bet).filter_by(user_id=referral.id))
        referral_bets = referral_bets.scalars().all()

        for referral_bet in referral_bets:
            round_stats = await round_stats_service.get_round_stats_by_round_id(referral_bet.round_id)
            if round_stats and referral_bet.card_id == round_stats.winner_card_id:
                total_referral_wins += round_stats.bones_coefficient * referral_bet.amount
                total_referral_wins += round_stats.not_coefficient * referral_bet.amount

    return {
        'total_bet_bones': total_bet_bones,
        'total_bet_not': total_bet_not,
        'total_won_bones': total_won_bones,
        'total_won_not': total_won_not,
        'total_referral_wins': total_referral_wins
    }




@user_api.post('/register-user')
async def register_user(
    username: str = Body(...),  # Ожидаем поле в теле запроса
    user_id: int = Body(...),  # Ожидаем поле в теле запроса
    client_ip: str = Body(None),  # Ожидаем поле в теле запроса
    db: AsyncSession = Depends(get_db),
    secret_key: str = Header(None, alias="Secret-Key"), # Секретный ключ передается через заголовок
    referral_code: str = Body(None)  # Ожидаем реферальный код в теле запроса (необязательный)
):
    # Проверка секретного ключа
    if secret_key != "HAHAHA":
        raise HTTPException(status_code=403, detail="Invalid secret key")

    user_service = UserService(db)

    # Проверяем, существует ли пользователь с данным user_id
    existing_user = await user_service.get_user_by_id(user_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Если передан реферальный код, ищем пользователя, который пригласил
    referred_by_user = None
    if referral_code:
        referred_by_user = await user_service.get_user_by_referral_code(referral_code)
        if not referred_by_user:
            raise HTTPException(status_code=404, detail="Referrer not found")

    try:
        # Генерация уникального токена
        permanent_token = await generate_permanent_token(user_service)

        # Генерация уникального реферального кода
        new_referral_code = await generate_referral_code(user_service)

        # Создаем нового пользователя
        new_user = await user_service.create_user(
            id=user_id,
            username=username,
            bones=100,
            not_tokens=100,
            referral_code=new_referral_code,
            referred_by=referred_by_user.referral_code if referred_by_user else None,
            token=permanent_token,
        )

        logging.info(f"Пользователь {username} успешно зарегистрирован.")
        return {"message": "User successfully registered", "user_id": new_user.id, "token": permanent_token}

    except Exception as e:
        logging.error(f"Ошибка при регистрации пользователя: {e}")
        raise HTTPException(status_code=500, detail="Error during registration")

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
