import logging
from flask import Flask, redirect, url_for, session, render_template
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

def create_tables():
    logging.info("Создание таблиц в базе данных...")
    try:
        with app.app_context():  # Включаем контекст приложения
            db.create_all()  # Создаем таблицы
        logging.info("Таблицы созданы успешно.")
    except Exception as e:
        logging.error(f"Ошибка при создании таблиц: {e}")

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

# Запуск приложения
if __name__ == '__main__':
    with app.app_context():
        create_tables()  # Создаем таблицы при запуске приложения
    print("Запуск Flask-приложения...")
    app.run(host='127.0.0.1', port=5000, debug=True)
