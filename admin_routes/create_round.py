import os
from datetime import datetime

from quart import Blueprint, render_template, request, jsonify
from sqlalchemy import update
from werkzeug.utils import secure_filename

from admin_routes.required import login_required
from app.db import get_db
from app.models import Round, Card

round = Blueprint('round', __name__)
# Создание нового раунда
@round.route('/create-round', methods=['GET', 'POST'])
@login_required
async def create_round():
    if request.method == 'POST':
        db = get_db()
        session = await db.__anext__()

        try:
            form = await request.form
            description = form.get('description')
            target = form.get('target')
            start_time = datetime.strptime(form.get('start_time'), "%Y-%m-%dT%H:%M")
            end_time = datetime.strptime(form.get('end_time'), "%Y-%m-%dT%H:%M")

            # Деактивируем все текущие раунды
            await session.execute(update(Round).values(is_active=False))
            await session.commit()

            # Создаем новый активный раунд
            new_round = Round(description=description, target=target, start_time=start_time, end_time=end_time, is_active=True)
            session.add(new_round)
            await session.commit()

            # Получаем и сохраняем изображения карточек
            upload_folder = 'static/uploads/'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            files = await request.files
            card1_image = files['card1_image']
            filename1 = secure_filename(card1_image.filename)
            await card1_image.save(os.path.join(upload_folder, filename1))

            card2_image = files['card2_image']
            filename2 = secure_filename(card2_image.filename)
            await card2_image.save(os.path.join(upload_folder, filename2))

            card3_image = files['card3_image']
            filename3 = secure_filename(card3_image.filename)
            await card3_image.save(os.path.join(upload_folder, filename3))

            # Добавляем карточки в базу данных
            card1 = Card(image_url=os.path.join(upload_folder, filename1), round_id=new_round.id)
            card2 = Card(image_url=os.path.join(upload_folder, filename2), round_id=new_round.id)
            card3 = Card(image_url=os.path.join(upload_folder, filename3), round_id=new_round.id)

            session.add_all([card1, card2, card3])
            await session.commit()

            return jsonify({"message": "Раунд успешно создан", "status": "success"}), 200

        except Exception as e:
            await session.rollback()
            return jsonify({"message": f"Ошибка при создании раунда: {str(e)}", "status": "error"}), 500

        finally:
            await session.close()

    return await render_template('admin/round_form.html')
