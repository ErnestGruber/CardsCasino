import logging
from flask import Flask, redirect, url_for, session, render_template
from config import Config
from models import db, User, Round, Card, Bet
from admin import AdminView

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
AdminView.init_app(app)
# Инициализация базы данных
db.init_app(app)

def create_tables():
    print("Создание таблиц в базе данных...")
    try:
        with app.app_context():  # Включаем контекст приложения
            db.create_all()  # Создаем таблицы
        print("Таблицы созданы успешно.")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")

# Маршрут для логина пользователя


@app.route('/game')
def game():
    return render_template('pages/game.html', round=round, cards=cards)


@app.route('/login/<int:user_id>')
def login(user_id):
    logging.info(f"Попытка входа пользователя с ID: {user_id}")
    user = User.query.filter_by(id=user_id).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        logging.info(f"Пользователь {user.username} вошел в систему.")
        return render_template('pages/index.html', username=user.username, not_tokens=user.not_tokens,
                               bones=user.bones)
    else:
        logging.info(f"Пользователь с ID {user_id} не найден!")
        return "Пользователь не найден!", 404


# Пример маршрута для фронта
@app.route('/welcome')
def welcome():
    if 'user_id' in session:
        return f"Добро пожаловать, {session['username']}!"
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():  # Включаем контекст приложения при запуске
        create_tables()  # Создаем таблицы при запуске приложения
    print("Запуск Flask-приложения...")
    app.run(host='127.0.0.1', port=5000, debug=True)
