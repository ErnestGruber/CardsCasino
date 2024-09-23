#
# from quart import Blueprint, jsonify, request
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.models import  Card
# from app.models.round import Round
#
# round_api = Blueprint('round_api', __name__)
#
# @round_api.route('/api/rounds', methods=['POST'])
# async def create_round():
#     description = request.form['description']
#     target = request.form['target']
#     start_time = request.form['start_time']
#     end_time = request.form['end_time']
#
#     async with AsyncSession(db.engine) as async_session:
#         new_round = Round(description=description, target=target, start_time=start_time, end_time=end_time)
#         async_session.add(new_round)
#         await async_session.commit()
#
#     return jsonify({'message': 'Round created successfully'}), 201
#
# @round_api.route('/api/rounds/<int:round_id>/cards', methods=['POST'])
# async def add_card(round_id):
#     async with AsyncSession(db.engine) as async_session:
#         round_ = await async_session.get(Round, round_id)
#         if not round_:
#             return jsonify({'error': 'Round not found'}), 404
#
#         image_url = request.form['image_url']
#         new_card = Card(image_url=image_url, round_id=round_id)
#         async_session.add(new_card)
#         await async_session.commit()
#
#     return jsonify({'message': 'Card added successfully'}), 201

