from quart import Blueprint, render_template, jsonify, redirect, url_for, request,  session as quart_session
from admin_routes.required import login_required

home = Blueprint('home', __name__)
@home.route('/', methods=['GET', 'POST'])
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
@home.route('/logout')
async def logout():
    quart_session.pop('logged_in', None)
    return redirect(url_for('login'))


# Главная страница админки
@home.route('/home')
@login_required
async def admin_home():
    return await render_template('admin/home.html')

