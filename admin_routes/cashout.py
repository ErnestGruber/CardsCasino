from quart import Blueprint, render_template,  jsonify, redirect, url_for

from admin_routes.required import login_required
from app.db import get_db
from app.services import CashoutService

cashout = Blueprint('cashout', __name__)

# Получение всех заявок на вывод для админки
@cashout.route('/cashouts', methods=['GET'])
@login_required
async def get_cashouts():
    db = get_db()
    session = await db.__anext__()
    try:
        cashout_service = CashoutService(session)

        # Получаем активные и завершённые заявки на вывод
        pending_cashouts = await cashout_service.get_pending_cashout_requests()
        complete_cashouts = await cashout_service.get_complete_cashout_requests()

        # Убедитесь, что 'await' используется перед render_template
        return await render_template(
            'admin/cashouts.html',
            pending_cashouts=pending_cashouts,
            complete_cashouts=complete_cashouts
        )
    finally:
        await session.close()

# Одобрение заявки на вывод средств
@cashout.route('/cashouts/approve/<int:cashout_id>', methods=['POST'])
@login_required
async def approve_cashout(cashout_id):
    db = get_db()
    session = await db.__anext__()
    try:
        cashout_service = CashoutService(session)
        success = await cashout_service.approve_cashout(cashout_id)

        if success:
            return redirect(url_for('get_cashouts'))
        return jsonify({"error": "Ошибка при обработке заявки"}), 500
    finally:
        await session.close()

# Отклонение заявки на вывод средств
@cashout.route('/cashouts/reject/<int:cashout_id>', methods=['POST'])
@login_required
async def reject_cashout(cashout_id):
    db = get_db()
    session = await db.__anext__()
    try:
        cashout_service = CashoutService(session)
        success = await cashout_service.reject_cashout(cashout_id)

        if success:
            return redirect(url_for('get_cashouts'))
        return jsonify({"error": "Ошибка при обработке заявки"}), 500
    finally:
        await session.close()