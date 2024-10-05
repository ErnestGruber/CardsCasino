import os
from datetime import datetime

from quart import Blueprint, render_template, request, jsonify
from sqlalchemy import update
from werkzeug.utils import secure_filename

from admin_routes.required import login_required
from app.db.session import AsyncSessionLocal
from app.services import RoundService, CardService


round = Blueprint('round', __name__)


# Создание нового раунда
@round.route('/create-round', methods=['GET', 'POST'])
@login_required
async def create_round():
    session = AsyncSessionLocal()

    try:
        if request.method == 'POST':
            round_service = RoundService(session)
            card_service = CardService(session)

            form = await request.form
            description = form.get('description')
            target = form.get('target')
            start_time = datetime.strptime(form.get('start_time'), "%Y-%m-%dT%H:%M")
            end_time = datetime.strptime(form.get('end_time'), "%Y-%m-%dT%H:%M")

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

            # Создаем новый активный раунд через сервис
            new_round = await round_service.create_round(
                description=description,
                target=target,
                start_time=start_time,
                end_time=end_time,
                card_urls=[],
                is_active=True
            )

            # Теперь добавляем карты в базу через CardService
            await card_service.create_card(image_url=os.path.join(upload_folder, filename1), round_id=new_round.id)
            await card_service.create_card(image_url=os.path.join(upload_folder, filename2), round_id=new_round.id)
            await card_service.create_card(image_url=os.path.join(upload_folder, filename3), round_id=new_round.id)

            return jsonify({"message": "Раунд и карточки успешно созданы", "status": "success"}), 200

    except Exception as e:
        await session.rollback()
        return jsonify({"message": f"Ошибка при создании раунда: {str(e)}", "status": "error"}), 500

    finally:
        await session.close()  # Закрываем сессию

    return await render_template('admin/round_form.html')