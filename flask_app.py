from functools import wraps
from quart import Quart, request, jsonify, render_template, redirect, url_for, session as quart_session, flash
from sqlalchemy import select, update
from app.db.session import get_db  # Подключение асинхронной сессии
from app.models import Round, Card
from app.services import RoundService, DepositService
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Quart(__name__)
app.secret_key = 'your_secret_key'  # Секретный ключ для работы с сессиями


# Декоратор для проверки авторизации
def login_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not quart_session.get('logged_in'):
            return redirect(url_for('login'))  # Перенаправляем на страницу логина
        return await func(*args, **kwargs)

    return wrapper


# Страница входа в систему
@app.route('/admin', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        form = await request.form
        username = form.get('username')
        password = form.get('password')
        # Пример простой авторизации
        if username == "admin" and password == "password":  # Замените на вашу логику проверки
            quart_session['logged_in'] = True
            return redirect(url_for('admin_home'))
        return "Неправильные учетные данные"

    return await render_template('admin/login.html')


# Маршрут для выхода из системы
@app.route('/admin/logout')
async def logout():
    quart_session.pop('logged_in', None)
    return redirect(url_for('login'))


# Главная страница админки
@app.route('/admin/home')
@login_required
async def admin_home():
    return await render_template('admin/home.html')


# Создание нового раунда
@app.route('/admin/create-round', methods=['GET', 'POST'])
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



# Статистика ставок
@app.route('/admin/bets-stats')
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


# Получение всех заявок с фильтрацией
@app.route('/admin/deposits', methods=['GET'])
@login_required
async def get_deposits():
    db = get_db()
    session = await db.__anext__()

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
@app.route('/admin/deposits/reject/<int:deposit_id>', methods=['POST'])
@login_required
async def reject_deposit(deposit_id):
    db = get_db()
    session = await db.__anext__()
    try:
        deposit_service = DepositService(session)
        success = await deposit_service.reject_deposit(deposit_id)

        if success:
            return redirect(url_for('get_deposits'))
        return jsonify({"error": "Ошибка при отклонении заявки"}), 500
    finally:
        await session.close()

# Одобрение заявки администратором
@app.route('/admin/deposits/approve/<int:deposit_id>', methods=['POST'])
@login_required
async def approve_deposit(deposit_id):
    db = get_db()
    session = await db.__anext__()  # Асинхронная сессия
    try:
        deposit_service = DepositService(session)

        # Одобрение заявки
        success = await deposit_service.approve_deposit(deposit_id)

        if success:
            return redirect(url_for('get_deposits'))  # Перенаправление на страницу заявок после успешного одобрения
        return jsonify({"error": "Ошибка при обработке заявки"}), 500
    finally:
        await session.close()

if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config as HyperConfig

    config = HyperConfig()
    config.bind = ["127.0.0.1:5000"]

    asyncio.run(serve(app, config))
