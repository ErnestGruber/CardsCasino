import logging
import signal
import sys

from fastapi import FastAPI

from app.api import game_api, user_api, deposit_api

app = FastAPI()

# Подключаем различные API
app.include_router(user_api, prefix="/api/users", tags=["Users"])
app.include_router(game_api, prefix="/api/game", tags=["Game"])
app.include_router(deposit_api, prefix="/api/deposit", tags=["Game"])
def signal_handler(sig, frame):
    print('Завершение работы сервера...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    import uvicorn
    print("START")
    uvicorn.run("client_api:app", host="127.0.0.1", port=8000)
