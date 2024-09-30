from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.session import get_db
from app.services import UserService, CardService, BetService, RoundService
from app.utils import process_referral_bonus
from app.utils.users import get_token_from_header
from app.api.schemas.game import GameResponseModel, BetRequest, BetResponseModel  # Импортируем схемы

game_api = APIRouter()


# получение активного раунда и карт для фронта
@game_api.get("/game", response_model=GameResponseModel)
async def get_game(db: AsyncSession = Depends(get_db)):
    round_service = RoundService(db)
    card_service = CardService(db)

    active_round = await round_service.get_active_round()
    if not active_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active round found")

    cards = await card_service.get_cards_by_round_id(active_round.id)

    cards_data = [{'id': card.id, 'image_url': card.image_url} for card in cards]

    return {
        'round': {'id': active_round.id, 'description': active_round.description, 'target': active_round.target},
        'cards': cards_data
    }


# Выбор карты и размещение ставки
@game_api.post("/choose_card/{card_id}", response_model=BetResponseModel)
async def choose_card(card_id: int, bet_request: BetRequest, db: AsyncSession = Depends(get_db), token_value: str = Depends(get_token_from_header)):
    user_service = UserService(db)
    card_service = CardService(db)
    bet_service = BetService(db)

    user = await user_service.get_user_by_token(token_value)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    card = await card_service.get_card_by_id(card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    existing_bet = await bet_service.get_bets_by_user_id(user.id)
    if existing_bet:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bet already placed")

    if bet_request.bet_type == "BONES":
        if user.bones < bet_request.bet_amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient BONES")
        await user_service.update_user_bones(user.id, -bet_request.bet_amount)
        await card_service.update_card(card_id, total_bones=card.total_bones + bet_request.bet_amount)
    elif bet_request.bet_type == "NOT":
        if user.not_tokens < bet_request.bet_amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient NOT tokens")
        await user_service.update_user_not_tokens(user.id, -bet_request.bet_amount)
        await card_service.update_card(card_id, total_not=card.total_not + bet_request.bet_amount)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bet type")

    await card_service.update_card(card_id, total_bank=card.total_bones + card.total_not)

    has_referrer = bool(user.referred_by)
    new_bet = await bet_service.create_bet(
        user_id=user.id,
        card_id=card_id,
        amount=bet_request.bet_amount,
        bet_type=bet_request.bet_type,
        round_id=bet_request.round_id,
        is_referral_bet=has_referrer
    )

    if has_referrer:
        referrer = await user_service.get_user_by_referral_code(user.referred_by)
        if referrer:
            await process_referral_bonus(user, referrer, bet_request.bet_amount, bet_request.bet_type, new_bet.id, db)

    return {"success": "Bet placed successfully", "bet_id": new_bet.id}