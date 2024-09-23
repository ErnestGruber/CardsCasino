import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7468220229:AAHQwWjFBKz5JeH8TjL-JfZGEgeF6oDL0mQ")
    UPLOAD_FOLDER = 'static/uploads'
    ADMIN_PASSWORD = "3dCKl}a%0g~H|@m$yY"