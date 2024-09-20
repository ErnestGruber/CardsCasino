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