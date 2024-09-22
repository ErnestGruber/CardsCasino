# Функция для проверки пароля
from functools import wraps

from flask import request, Response


def check_admin_password(password):
    return password == "3dCKl}a%0g~H|@m$yY"

# Декоратор для проверки аутентификации
def admin_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_admin_password(auth.password):
            return Response(
                'Неверный пароль. Доступ запрещен.', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'}
            )
        return f(*args, **kwargs)
    return decorated_function