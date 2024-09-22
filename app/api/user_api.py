import logging
import secrets

from quart import Blueprint, jsonify, session
from sqlalchemy import select
from flask import jsonify, request

from app.models import User, db,ReferralStats
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.users import register_user, get_ip

user_api = Blueprint('user_api', __name__)

@user_api.route('/api/login/<string:token_value>', methods=['POST'])
async def api_login(token_value):
    logging.info(f"Попытка входа с токеном: {token_value}")

    async with AsyncSession(db.engine) as async_session:
        # Проверяем, существует ли пользователь с данным токеном
        result = await async_session.execute(select(User).filter_by(token=token_value))
        user = result.scalars().first()

        # Если пользователя нет, регистрируем его
        if not user:
            username = request.json.get('username')
            user_id = request.json.get('user_id')
            referral_code = request.json.get('referral_code')
            client_ip = await get_ip(request)  # Получаем IP пользователя

            # Вызываем асинхронную функцию регистрации
            user = await register_user(async_session, username, user_id, client_ip, referral_code)

            if not user:
                return jsonify({'error': 'Ошибка регистрации пользователя'}), 500

        # Сохраняем информацию о пользователе в сессии
        session['user_id'] = user.id
        session['username'] = user.username

        logging.info(f"Пользователь {user.username} успешно вошел в систему.")

        # Обработка реферального кода, если он передан (для существующих пользователей)
        referral_code = request.json.get('referral_code')
        if referral_code and not user.referred_by:
            referrer = await async_session.execute(select(User).filter_by(referral_code=referral_code))
            referrer = referrer.scalars().first()

            if referrer and referrer.id != user.id:
                user.referred_by = referrer.referral_code
                await async_session.commit()

        return jsonify({
            'username': user.username,
            'not_tokens': user.not_tokens,
            'bones': user.bones,
            'is_admin': user.is_admin
        }), 200


@user_api.route('/api/referrals', methods=['GET'])
async def get_referral_stats():
    # Получаем токен из заголовка
    token_value = request.headers.get('Authorization')

    if not token_value:
        return jsonify({'error': 'Токен не предоставлен'}), 401

    # Удаляем "Bearer " из значения заголовка, если используется формат "Bearer <token>"
    if token_value.startswith('Bearer '):
        token_value = token_value.split(' ')[1]

    # Ищем пользователя по токену
    async with AsyncSession(db.engine) as async_session:
        result = await async_session.execute(select(User).filter_by(token=token_value))
        user = result.scalars().first()

        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404

        # Ищем всех рефералов пользователя
        referrals_query = await async_session.execute(select(User).filter_by(referred_by=user.referral_code))
        referrals = referrals_query.scalars().all()

        referral_stats = []
        total_brought_in = 0

        # Для каждого реферала собираем информацию о ставках и принесенных бонусах
        for referral in referrals:
            stats_query = await async_session.execute(select(ReferralStats).filter_by(referrer_id=user.id, referral_id=referral.id))
            stats = stats_query.scalars().all()

            total_for_referral = sum(stat.referrer_bonus for stat in stats)
            total_brought_in += total_for_referral

            referral_stats.append({
                'referral_id': referral.id,
                'referral_username': referral.username,
                'brought_in_bonus': total_for_referral
            })

        return jsonify({
            'total_brought_in': total_brought_in,
            'referrals': referral_stats
        }), 200

def generate_referral_code():
    return secrets.token_hex(5)
# Создаем уникальный токен для пользователя при регистрации
def generate_permanent_token():
    return secrets.token_urlsafe(16)
def generate_referral_link(user):
    referral_code = user.referral_code
    referral_link = f"https://t.me/YourTelegramBot?start={referral_code}"
    return referral_link