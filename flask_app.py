
from quart import Quart
from admin_routes import cashout, deposit, bets_stats_bp, round, home

app = Quart(__name__)
app.secret_key = 'your_secret_key'  # Секретный ключ для работы с сессиями


app.register_blueprint(deposit, url_prefix='/admin')
app.register_blueprint(bets_stats_bp, url_prefix='/admin')
app.register_blueprint(cashout, url_prefix='/admin')
app.register_blueprint(round, url_prefix='/admin')
app.register_blueprint(home, url_prefix='/admin')

if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config as HyperConfig

    config = HyperConfig()
    config.bind = ["127.0.0.1:5000"]

    asyncio.run(serve(app, config))
