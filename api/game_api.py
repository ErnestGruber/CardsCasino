from quart import Blueprint, jsonify, request, session
# from models import Round, Card, Bet, db, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from services import process_referral_bonus

game_api = Blueprint('game_api', __name__)


# получение активного раунда и карт для фронта
@game_api.route('/api/game', methods=['GET'])
async def get_game():
    async with AsyncSession(db.engine) as async_session:
        active_round = await async_session.execute(select(Round).filter_by(is_active=True))
        active_round = active_round.scalars().first()

        if active_round:
            cards = await async_session.execute(select(Card).filter_by(round_id=active_round.id))
            cards = cards.scalars().all()
            cards_data = [{'id': card.id, 'image_url': card.image_url, 'total_bones': card.total_bones,
                           'total_not': card.total_not} for card in cards]
            return jsonify(
                {'round': {'id': active_round.id, 'description': active_round.description}, 'cards': cards_data})
        else:
            return jsonify({'error': 'No active round found'}), 404


@game_api.route('/api/choose_card/<int:card_id>', methods=['POST'])
async def choose_card(card_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    async with AsyncSession(db.engine) as async_session:
        user = await async_session.get(User, session['user_id'])
        card = await async_session.get(Card, card_id)

        if not card:
            return jsonify({'error': 'Card not found'}), 404

        round_id = request.form['round_id']
        bet_type = request.form['bet_type']
        bet_amount = int(request.form['bet_amount'])

        # Асинхронная проверка, есть ли уже ставка
        existing_bet = await get_bet(round_id, user.id, async_session)
        if existing_bet:
            return jsonify({'error': 'Bet already placed'}), 400

        if bet_type == "bones":
            if user.bones < bet_amount:
                return jsonify({'error': 'Insufficient BONES'}), 400
            user.bones -= bet_amount
            card.total_bones += bet_amount
        elif bet_type == "not_tokens":
            if user.not_tokens < bet_amount:
                return jsonify({'error': 'Insufficient NOT tokens'}), 400
            user.not_tokens -= bet_amount
            card.total_not += bet_amount

        if user.referred_by:
            referrer = User.query.filter_by(referral_code=user.referred_by).first()
            if referrer:
                process_referral_bonus(user, referrer, bet_amount, bet_type)

        card.total_bank = card.total_bones + card.total_not

        new_bet = Bet(user_id=user.id, card_id=card_id, amount=bet_amount, round_id=round_id, bet_type=bet_type)
        async_session.add(new_bet)
        await async_session.commit()

        return jsonify({'success': 'Bet placed successfully'}), 200


async def get_bet(round_id: int, user_id: int, session: AsyncSession):
    result = await session.execute(select(Bet).filter_by(round_id=round_id, user_id=user_id))
    return result.scalars().first()
