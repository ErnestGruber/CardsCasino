from functools import wraps
from quart import redirect, url_for, session as quart_session

def login_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not quart_session.get('logged_in'):
            return redirect(url_for('login'))  # Перенаправляем на страницу логина
        return await func(*args, **kwargs)

    return wrapper