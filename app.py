import logging
from flask import Flask, session, render_template, request
from config import Config
from models import db, Round, Card, User, Bet, Token
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


@app.route('/login/<string:token_value>', methods=['GET', 'POST'])
def login(token_value):
    logging.info(f"Попытка входа с токеном: {token_value}")

    # Проверяем, существует ли токен и не истек ли его срок действия
    token = Token.query.filter_by(token=token_value).first()
    if not token or not token.is_valid():
        return "Неверный или просроченный токен", 403

    user = User.query.filter_by(id=token.user_id).first()
    if not user:
        logging.error(f"Пользователь с ID {token.user_id} не найден!")
        return "Пользователь не найден!", 404

    session['user_id'] = user.id
    session['username'] = user.username

    # Если это GET-запрос, просто рендерим страницу
    if request.method == 'GET':
        return render_template('pages/index.html',
                               username=user.username,
                               not_tokens=user.not_tokens,
                               bones=user.bones,
                               is_admin=user.is_admin)

    session['user_id'] = user.id
    session['username'] = user.username
    logging.info(f"Пользователь {user.username} вошел в систему.")

    # Если это POST-запрос, проверяем реферальный код
    if request.method == 'POST':
        referral_code = request.form.get('referral_code')
        if referral_code and not user.referred_by:
            referrer = User.query.filter_by(referral_code=referral_code).first()
            if referrer and referrer.id != user.id:
                user.referred_by = referrer.referral_code
                db.session.commit()
                # Добавляем бонусы рефереру
                process_referral_bonus(user, referrer)
                return "Реферальный код принят!"
            else:
                return "Неверный реферальный код или вы не можете использовать свой собственный код."

    return "Ошибка при обработке запроса.", 400



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

