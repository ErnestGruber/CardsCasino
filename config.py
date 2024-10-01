import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URL = "postgresql+asyncpg://postgres:2281337@localhost:5432/royal"
    print(DATABASE_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN", "7468220229:AAHQwWjFBKz5JeH8TjL-JfZGEgeF6oDL0mQ"
    UPLOAD_FOLDER = 'static/uploads'
    ADMIN_PASSWORD = "3dCKl}a%0g~H|@m$yY"