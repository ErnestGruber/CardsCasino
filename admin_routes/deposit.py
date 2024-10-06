from datetime import datetime

from quart import Blueprint, render_template, jsonify, redirect, url_for, request

from admin_routes.required import login_required
from app.db import get_db
from app.db.session import AsyncSessionLocal
from app.services import DepositService

deposit = Blueprint('deposits', __name__)

# Получение всех заявок с фильтрацией
@deposit.route('/deposits', methods=['GET'])
@login_required
async def get_deposits():
    session = AsyncSessionLocal()

    # Получаем параметры фильтрации
    created_from = request.args.get('created_from')
    created_to = request.args.get('created_to')
    approved_from = request.args.get('approved_from')
    approved_to = request.args.get('approved_to')

    if created_from:
        created_from = datetime.strptime(created_from, '%Y-%m-%dT%H:%M')
    if created_to:
        created_to = datetime.strptime(created_to, '%Y-%m-%dT%H:%M')
    if approved_from:
        approved_from = datetime.strptime(approved_from, '%Y-%m-%dT%H:%M')
    if approved_to:
        approved_to = datetime.strptime(approved_to, '%Y-%m-%dT%H:%M')

    try:
        deposit_service = DepositService(session)
        pending_deposits = await deposit_service.get_pending_deposits(created_from, created_to)
        complete_deposits = await deposit_service.get_complete_deposits(approved_from, approved_to)

        return await render_template(
            'admin/deposits.html',
            pending_deposits=pending_deposits,
            complete_deposits=complete_deposits
        )
    finally:
        await session.close()


# Отклонение заявки администратором
@deposit.route('/deposits/reject/<int:deposit_id>', methods=['POST'])
@login_required
async def reject_deposit(deposit_id):
    session = AsyncSessionLocal()
    try:
        deposit_service = DepositService(session)
        success = await deposit_service.reject_deposit(deposit_id)

        if success:
            return redirect(url_for('get_deposits'))
        return jsonify({"error": "Ошибка при отклонении заявки"}), 500
    finally:
        await session.close()


# Одобрение заявки администратором
@deposit.route('/deposits/approve/<int:deposit_id>', methods=['POST'])
@login_required
async def approve_deposit(deposit_id):
    session = AsyncSessionLocal()
    try:
        deposit_service = DepositService(session)

        # Одобрение заявки
        success = await deposit_service.approve_deposit(deposit_id)

        if success:
            return redirect(url_for('get_deposits'))  # Перенаправление на страницу заявок после успешного одобрения
        return jsonify({"error": "Ошибка при обработке заявки"}), 500
    finally:
        await session.close()