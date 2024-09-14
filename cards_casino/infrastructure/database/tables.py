from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

# Модель пользователя
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    bones = db.Column(db.Integer, default=100)  # Начальные очки BONES
    not_tokens = db.Column(db.Integer, default=0)  # Токены NOT
    woof_tokens = db.Column(db.Integer, default=0)  # Токены WOOF (для будущего расширения)
    referral_code = db.Column(db.String(100), unique=True)  # Уникальный реферальный код
    referred_by = db.Column(db.String(100), db.ForeignKey('user.referral_code'), nullable=True)  # Реферер
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Связь с рефералами
    referrals = db.relationship('User', backref=db.backref('referrer', remote_side=[referral_code]))
    bets = db.relationship('Bet', backref='user', lazy=True)  # Ставки игрока

    def __init__(self, username, referral_code, referred_by=None):
        self.username = username
        self.referral_code = referral_code
        self.referred_by = referred_by

# Модель раунда
class Round(db.Model):
    __tablename__ = 'round'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)  # Описание раунда
    target = db.Column(db.String(50), nullable=False)  # Цель раунда: популярная, средняя или непопулярная карточка
    start_time = db.Column(db.DateTime, nullable=False)  # Время начала раунда
    end_time = db.Column(db.DateTime, nullable=False)  # Время окончания раунда
    results_calculated = db.Column(db.Boolean, default=False)  # Подсчитаны ли результаты
    cards = db.relationship('Card', backref='round', lazy=True)  # Связь с карточками

    def __init__(self, description, target, start_time, end_time):
        self.description = description
        self.target = target
        self.start_time = start_time
        self.end_time = end_time

# Модель карточки
class Card(db.Model):
    __tablename__ = 'card'

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)  # URL изображения
    text = db.Column(db.String(255), nullable=False)  # Описание/текст карточки
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)  # Привязка к раунду
    total_bones = db.Column(db.Integer, default=0)  # Общее количество BONES, поставленных на карточку
    bets = db.relationship('Bet', backref='card', lazy=True)  # Ставки на карточку

    def __init__(self, image_url, text, round_id):
        self.image_url = image_url
        self.text = text
        self.round_id = round_id

# Модель ставки
class Bet(db.Model):
    __tablename__ = 'bet'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Кто сделал ставку
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)  # На какую карточку была сделана ставка
    bones = db.Column(db.Integer, nullable=False)  # Количество BONES, поставленных на карточку
    placed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, user_id, card_id, bones):
        self.user_id = user_id
        self.card_id = card_id
        self.bones = bones

# Модель для управления реферальной системой
class ReferralBonus(db.Model):
    __tablename__ = 'referral_bonus'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Пользователь, получивший бонус
    referred_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Приглашенный пользователь
    bonus_bones = db.Column(db.Integer, default=0)  # Количество бонусных BONES

    referred_user = db.relationship('User', foreign_keys=[referred_user_id])
    user = db.relationship('User', foreign_keys=[user_id])

    def __init__(self, user_id, referred_user_id, bonus_bones):
        self.user_id = user_id
        self.referred_user_id = referred_user_id
        self.bonus_bones = bonus_bones
