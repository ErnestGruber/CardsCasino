import logging
from flask import Flask, redirect, url_for, session
from config import Config
from models import db, User, Round, Card, Bet
from admin import setup_admin

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Инициализация базы данных
db.init_app(app)

# Инициализация админской панели
setup_admin(app)

@app.before_first_request
def create_tables():
    logging.info("Создание таблиц в базе данных...")
    try:
        db.create_all()  # Создаем таблицы
        logging.info("Таблицы созданы успешно.")
    except Exception as e:
        logging.info(f"Ошибка при создании таблиц: {e}")

# Маршрут для логина пользователя
@app.route('/login/<int:user_id>')
def login(user_id):
    logging.info(f"Попытка входа пользователя с ID: {user_id}")
    user = User.query.filter_by(id=user_id).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        logging.info(f"Пользователь {user.username} вошел в систему.")
        return redirect(url_for('welcome'))
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
    print("Запуск Flask-приложения...")
    app.run(host='127.0.0.1', port=9999, debug=True)
