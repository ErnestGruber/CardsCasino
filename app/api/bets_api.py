import logging
import secrets

from fastapi import APIRouter, Request, Depends, HTTPException, Header, Body, Response
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Bet, ReferralStats
from app.services import UserService, ReferralStatsService, RoundStatsService, BetService, CardService
from app.utils.users import get_token_from_header

bets_stats_api = APIRouter()

@bets_stats_api.get('/user-bet-stats')
async def get_user_bet_stats(
    db: AsyncSession = Depends(get_db),
    token_value: str = Depends(get_token_from_header)
):
    # Инициализация сервисов
    bet_service = BetService(db)
    card_service = CardService(db)
    round_stats_service = RoundStatsService(db)

    # Получаем пользователя по токену
    user_service = UserService(db)
    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем ставки пользователя
    user_bets = await bet_service.get_bets_by_user_id(user.id)

    # Структура для хранения данных о раундах
    rounds_data = []

    for bet in user_bets:
        round_data = {
            "round_id": bet.round_id,
        }

        # Получаем информацию о карте пользователя, если она есть
        if bet.card_id:
            card = await card_service.get_card_by_id(bet.card_id)
            round_data["bet_user"] = {
                "card_id": bet.card_id,
                "won_amount": bet.amount  # Здесь нужно будет заменить, если есть другой способ вычисления выигрыша
            }

        # Получаем данные о победной карте и статистике по раунду
        round_stats = await round_stats_service.get_round_stats_by_round_id(bet.round_id)
        if round_stats:
            round_data["winner_card_id"] = round_stats.winner_card_id

            # Получаем карты и процентили для раунда
            cards = await card_service.get_cards_by_round_id(bet.round_id)
            round_data["round_stats"] = {
                "card_1_id": cards[0].id if len(cards) > 0 else None,
                "card1procentile": cards[0].total_bank if len(cards) > 0 else None,
                "card_2_id": cards[1].id if len(cards) > 1 else None,
                "card2procentile": cards[1].total_bank if len(cards) > 1 else None,
                "card_3_id": cards[2].id if len(cards) > 2 else None,
                "card3procentile": cards[2].total_bank if len(cards) > 2 else None,
            }

        rounds_data.append(round_data)

    return rounds_data


