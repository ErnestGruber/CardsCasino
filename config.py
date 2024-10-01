import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
    f"@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
)

    # Проверка того, что переменные окружения загружаются
    print(f"DATABASE_URL: {DATABASE_URL}")
    print(f"DATABASE_USER: {os.getenv('DATABASE_USER')}")
    print(f"DATABASE_PASSWORD: {os.getenv('DATABASE_PASSWORD')}")
    print(f"DATABASE_HOST: {os.getenv('DATABASE_HOST')}")
    print(f"DATABASE_PORT: {os.getenv('DATABASE_PORT')}")
    print(f"DATABASE_NAME: {os.getenv('DATABASE_NAME')}")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7468220229:AAHQwWjFBKz5JeH8TjL-JfZGEgeF6oDL0mQ")
    UPLOAD_FOLDER = 'static/uploads'
    ADMIN_PASSWORD = "3dCKl}a%0g~H|@m$yY"