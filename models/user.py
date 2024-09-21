import secrets

from flask_sqlalchemy import SQLAlchemy
import datetime

from . import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    bones = db.Column(db.Integer, default=100)  # Баланс BONES
    not_tokens = db.Column(db.Integer, default=0)  # Баланс NOT токенов
    bonus_not_tokens = db.Column(db.Integer, default=0)  # Бонусные NOT токены (от рефералов)
    referral_code = db.Column(db.String(100), unique=True)  # Уникальный реферальный код
    referred_by = db.Column(db.String(100), db.ForeignKey('user.referral_code'), nullable=True)  # Реферал
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # Дата регистрации
    token = db.Column(db.String(32), unique=True, nullable=False)  # Токен
    is_admin = db.Column(db.Boolean, default=False)  # Администратор или нет
    wallet_address = db.Column(db.String(255), default="0xDefaultWallet")  # Адрес кошелька

    # Рефералы и пригласивший
    referrals = db.relationship('User', backref=db.backref('referrer', remote_side=[referral_code]))
    bets = db.relationship('Bet', backref='user', lazy=True)
    def __init__(self, bones, not_tokens, token, username, referral_code=None, referred_by=None, id=None, is_admin=False, wallet_address="0xDefaultWallet"):
        self.id = id
        self.bones = bones
        self.not_tokens = not_tokens
        self.username = username
        self.referral_code = referral_code or secrets.token_hex(5)
        self.referred_by = referred_by
        self.is_admin = is_admin
        self.wallet_address = wallet_address