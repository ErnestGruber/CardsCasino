import secrets

from quart import Blueprint, jsonify, session
from sqlalchemy import select

from models import User, db
from sqlalchemy.ext.asyncio import AsyncSession

user_api = Blueprint('user_api', __name__)

@user_api.route('/api/login/<string:token>', methods=['GET'])
async def login(token):
    async with AsyncSession(db.engine) as async_session:
        # Ищем пользователя по токену
        result = await async_session.execute(select(User).filter_by(token=token))
        user = result.scalars().first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({
                'username': user.username,
                'not_tokens': user.not_tokens,
                'bones': user.bones,
                'is_admin': user.is_admin
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404

def generate_referral_code():
    return secrets.token_hex(5)
# Создаем уникальный токен для пользователя при регистрации
def generate_permanent_token():
    return secrets.token_urlsafe(16)
def generate_referral_link(user):
    referral_code = user.referral_code
    referral_link = f"https://t.me/YourTelegramBot?start={referral_code}"
    return referral_link