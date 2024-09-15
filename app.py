import logging
from flask import Flask, redirect, url_for, session, render_template, request
from config import Config
from models import db, User, Round, Card, Bet
from admin import setup_admin  # Теперь просто импортируем функцию настройки админки

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Инициализация базы данных
db.init_app(app)

# Инициализация админ-панели
setup_admin(app)  # Настраиваем админку здесь после инициализации приложения

@app.route('/game')
def game():
    # Получаем активный раунд
    active_round = Round.query.filter_by(is_active=True).first()

    if active_round:
        cards = Card.query.filter_by(round_id=active_round.id).all()
        return render_template('pages/game.html', round=active_round, cards=cards)
    else:
        return "Нет активного раунда", 404

def create_tables():
    print("Создание таблиц в базе данных...")
    try:
        with app.app_context():  # Включаем контекст приложения
            db.create_all()  # Создаем таблицы
        print("Таблицы созданы успешно.")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")

@app.route('/login/<int:user_id>')
def login(user_id):
    logging.info(f"Попытка входа пользователя с ID: {user_id}")
    user = User.query.filter_by(id=user_id).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        logging.info(f"Пользователь {user.username} вошел в систему.")
        return render_template('pages/index.html', username=user.username, not_tokens=user.not_tokens, bones=user.bones)
    else:
        logging.info(f"Пользователь с ID {user_id} не найден!")
        return "Пользователь не найден!", 404


# app.py

@app.route('/choose_card/<int:card_id>', methods=['POST'])
def choose_card(card_id):
    if 'user_id' not in session:
        return "Вы не авторизованы!", 403

    user = User.query.get(session['user_id'])
    card = Card.query.get(card_id)

    if not card:
        return "Карточка не найдена!", 404

    bet_amount = int(request.form['bet_amount'])

    # Проверка, есть ли уже ставка на этот раунд
    existing_bet = Bet.query.filter_by(user_id=user.id, card_id=card_id).first()
    if existing_bet:
        return "Вы уже сделали ставку на эту карточку!", 400

    # Проверка, хватает ли у пользователя BONES
    if user.bones < bet_amount:
        return "У вас недостаточно BONES для этой ставки!", 400

    # Обновляем данные пользователя и карточки
    user.bones -= bet_amount
    card.total_bones += bet_amount

    new_bet = Bet(user_id=user.id, card_id=card_id, bones=bet_amount)
    db.session.add(new_bet)
    db.session.commit()

    return "Вы успешно проголосовали за карточку!", 200

# Запуск приложения
if __name__ == '__main__':
    with app.app_context():
        create_tables()  # Создаем таблицы при запуске приложения
    print("Запуск Flask-приложения...")
    app.run(host='127.0.0.1', port=5000, debug=True)
