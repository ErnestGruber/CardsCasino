from datetime import datetime

from quart import Blueprint, render_template, jsonify, redirect, url_for
from sqlalchemy import select

from admin_routes.required import login_required
from app.db import get_db
from app.models import Card, Round
from app.services import RoundService

bets_stats_bp = Blueprint('bets_stats', __name__)

@bets_stats_bp.route('/bets-stats' , methods=['GET', 'POST'])
@login_required
async def bets_stats():
    db = get_db()
    session = await db.__anext__()
    round_service = RoundService(session)

    try:
        active_round = await round_service.get_active_round()

        if not active_round:
            return jsonify({"message": "Нет активного раунда для отображения статистики."})

        cards_result = await session.execute(select(Card).where(Card.round_id == active_round.id))
        cards = cards_result.scalars().all()

        total_bones = sum(card.total_bones for card in cards)
        total_not = sum(card.total_not for card in cards)
        total_bank = total_bones + total_not

        stats = []
        for card in cards:
            card_bank = card.total_bones + card.total_not
            percentage = (card_bank / total_bank) * 100 if total_bank > 0 else 0
            stats.append({
                'image_url': card.image_url,
                'total_bones': card.total_bones,
                'total_not': card.total_not,
                'percentage': round(percentage, 2)
            })

        return await render_template('admin/bets_stats.html', stats=stats, total_bank=total_bank)

    finally:
        await session.close()

@bets_stats_bp.route('/admin/end-round', methods=['POST'])
@login_required
async def end_round():
    db = get_db()
    session = await db.__anext__()
    try:
        round_service = RoundService(session)

        # Получаем активный раунд
        active_round = await round_service.get_active_round()
        if not active_round:
            return jsonify({"error": "Нет активного раунда"}), 400

        # Завершаем активный раунд
        await round_service.end_round(active_round.id)
        return redirect(url_for('admin_rounds'))  # Перенаправление на страницу раундов
    finally:
        await session.close()