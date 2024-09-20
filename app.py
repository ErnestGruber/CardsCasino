import logging
from flask import Flask, redirect, url_for, session, render_template, request
from config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import db, Round, Card, User, Bet
from flask_caching import Cache


from flask_migrate import Migrate

from services import process_referral_bonus

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
migrate = Migrate(app, db)

# Инициализация базы данных
db.init_app(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
@app.route('/game')
def game():
    active_round = Round.query.filter_by(is_active=True).first()

    if active_round:
        cards = Card.query.filter_by(round_id=active_round.id).all()
        return render_template('pages/game.html', round=active_round, cards=cards)
    else:
        return "Нет активного раунда", 404


@app.route('/login/<int:user_id>')
def login(user_id):
    logging.info(f"Попытка входа пользователя с ID: {user_id}")
    user = User.query.filter_by(id=user_id).first()

    if user:
        session['user_id'] = user.id
        session['username'] = user.username

        # Проставляем флаг админа, если имя пользователя равно GertyHelher
        if user.username == 'GertyHelher':
            user.is_admin = True
            db.session.commit()

        logging.info(f"Пользователь {user.username} вошел в систему.")
        return render_template('pages/index.html',
                               username=user.username,
                               not_tokens=user.not_tokens,
                               bones=user.bones,
                               is_admin=user.is_admin)
    else:
        logging.info(f"Пользователь с ID {user_id} не найден!")
        return "Пользователь не найден!", 404

# app.py

@app.route('/choose_card/<int:card_id>', methods=['POST'])
def choose_card(card_id):
    print(f"Получен запрос на карточку ID: {card_id}")
    print(f"Пользователь ID: {session.get('user_id')}")

    if 'user_id' not in session:
        print("Ошибка: пользователь не авторизован")
        return "Вы не авторизованы!", 403

    user = User.query.get(session['user_id'])
    card = Card.query.get(card_id)
    round_id = request.form['round_id']
    bet_type = request.form['bet_type']
    bet_amount = int(request.form['bet_amount'])

    print(f"Ставка: {bet_amount}, Тип ставки: {bet_type}, Раунд: {round_id}")

    if not card:
        print("Ошибка: карточка не найдена")
        return "Карточка не найдена!", 404

    # Проверка, есть ли уже ставка на этот раунд
    existing_bet = Bet.query.filter_by(user_id=user.id, card_id=card_id, round_id=round_id).first()
    if existing_bet:
        print("Ошибка: пользователь уже сделал ставку")
        return "Вы уже сделали ставку на эту карточку!", 400

    # Проверяем баланс пользователя
    if bet_type == "bones":
        if user.bones < bet_amount:
            print("Ошибка: недостаточно BONES")
            return "У вас недостаточно BONES для этой ставки!", 400
        user.bones -= bet_amount
    elif bet_type == "not_tokens":
        if user.not_tokens < bet_amount:
            print("Ошибка: недостаточно NOT Tokens")
            return "У вас недостаточно NOT Tokens для этой ставки!", 400
        user.not_tokens -= bet_amount
    else:
        print("Ошибка: неверный тип ставки")
        return "Неверный тип ставки!", 400

    # Создаем новую ставку
    new_bet = Bet(user_id=user.id, card_id=card_id, amount=bet_amount, round_id=round_id, bet_type=bet_type)
    db.session.add(new_bet)

    # Начисляем бонусы пригласившему пользователя (рефереру)
    referrer = user.referrer
    if referrer:
        process_referral_bonus(user, referrer, bet_amount, bet_type)

    db.session.commit()

    print("Ставка успешно сделана")
    return "Вы успешно проголосовали за карточку!", 200

# После того, как приложение создано и инициализировано, импортируем setup_admin
from admin import setup_admin

# Запуск админки после инициализации приложения
setup_admin(app)

# Запуск приложения
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаем таблицы при запуске приложения
    print("Запуск Flask-приложения...")
    app.run(host='127.0.0.1', port=5000, debug=True)

