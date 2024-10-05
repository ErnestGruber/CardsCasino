import logging
import signal
import sys
from fastapi import FastAPI
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.api import game_api, user_api, deposit_api, bets_stats_api, cashout_api

app = FastAPI( title="Deposit API",
    description="API для обработки запросов на пополнение и взаимодействия с пользователями",
    version="1.0.0",
    contact={
        "name": "Поддержка",
        "email": "support@example.com",
    },
    docs_url="/docs",          # Можно изменить при необходимости
    redoc_url="/redoc",        # Можно изменить при необходимости
    openapi_url="/openapi.json",)

app.add_middleware(HTTPSRedirectMiddleware)

# Подключаем различные API
app.include_router(user_api, prefix="/api/users", tags=["Users"])
app.include_router(game_api, prefix="/api/game", tags=["Game"])
app.include_router(deposit_api, prefix="/api/deposit", tags=["Deposit"])
app.include_router(bets_stats_api, prefix="/api/bets_api", tags=["Bets"])
app.include_router(cashout_api, prefix="/api/cashout", tags=["Cashouts"])

def signal_handler(sig, frame):
    print('Завершение работы сервера...')
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    import uvicorn
    print("START")
    uvicorn.run("client_api:app", host="127.0.0.1", port=8000)
