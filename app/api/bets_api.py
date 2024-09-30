from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services import UserService, RoundStatsService, BetService, CardService
from app.utils.users import get_token_from_header
from app.api.schemas.bets import RoundsDataResponseModel, RoundDataModel  # Импортируем схемы

bets_stats_api = APIRouter()

@bets_stats_api.get('/user-bet-stats', response_model=RoundsDataResponseModel)
async def get_user_bet_stats(
    db: AsyncSession = Depends(get_db),
    token_value: str = Depends(get_token_from_header)
):
    bet_service = BetService(db)
    card_service = CardService(db)
    round_stats_service = RoundStatsService(db)

    user_service = UserService(db)
    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_bets = await bet_service.get_bets_by_user_id(user.id)
    rounds_data = []

    for bet in user_bets:
        round_data = RoundDataModel(
            round_id=bet.round_id,
            bet_user=None,
            winner_card_id=None,
            round_stats=None
        )

        if bet.card_id:
            card = await card_service.get_card_by_id(bet.card_id)
            round_data.bet_user = {
                "card_id": bet.card_id,
                "won_amount": bet.amount
            }

        round_stats = await round_stats_service.get_round_stats_by_round_id(bet.round_id)
        if round_stats:
            round_data.winner_card_id = round_stats.winner_card_id

            cards = await card_service.get_cards_by_round_id(bet.round_id)
            round_data.round_stats = {
                "card_1_id": cards[0].id if len(cards) > 0 else None,
                "card1procentile": cards[0].total_bank if len(cards) > 0 else None,
                "card_2_id": cards[1].id if len(cards) > 1 else None,
                "card2procentile": cards[1].total_bank if len(cards) > 1 else None,
                "card_3_id": cards[2].id if len(cards) > 2 else None,
                "card3procentile": cards[2].total_bank if len(cards) > 2 else None,
            }

        rounds_data.append(round_data)

    return RoundsDataResponseModel(rounds=rounds_data)
