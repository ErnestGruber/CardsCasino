from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

# Модель пользователя
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    bones = db.Column(db.Integer, default=100)  # Начальные очки BONES
    not_tokens = db.Column(db.Integer, default=0)  # Токены NOT
    referral_code = db.Column(db.String(100), unique=True)  # Уникальный реферальный код
    referred_by = db.Column(db.String(100), db.ForeignKey('user.referral_code'), nullable=True)  # Реферер
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    is_admin = db.Column(db.Boolean, default=False)  # Поле, указывающее, является ли пользователь администратором
    wallet_address = db.Column(db.String(255), default="0xDefaultWallet")  # Адрес кошелька пользователя

    # Связь с рефералами
    referrals = db.relationship('User', backref=db.backref('referrer', remote_side=[referral_code]))
    bets = db.relationship('Bet', backref='user', lazy=True)  # Ставки игрока

    def __init__(self, bones, not_tokens, username, referral_code=None, referred_by=None, id=None, is_admin=False,
                 wallet_address="0xDefaultWallet"):
        self.id = id
        self.bones = bones
        self.not_tokens = not_tokens
        self.username = username
        self.referral_code = referral_code
        self.referred_by = referred_by
        self.is_admin = is_admin
        self.wallet_address = wallet_address

# Модель раунда
class Round(db.Model):
    __tablename__ = 'round'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    target = db.Column(db.String(255), nullable=False)  # Цель раунда (популярная, средняя, непопулярная)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)  # Новый флаг, указывающий, активен ли раунд
    cards = db.relationship('Card', backref='round', lazy=True)

    def __init__(self, description, target, start_time, end_time, is_active=False):
        self.description = description
        self.target = target
        self.start_time = start_time
        self.end_time = end_time
        self.is_active = is_active


# Модель карточки
class Card(db.Model):
    __tablename__ = 'card'

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)  # URL изображения карточки
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)  # Привязка к раунду
    total_bones = db.Column(db.Integer, default=0)  # Общее количество BONES
    total_not = db.Column(db.Integer, default=0)  # Общее количество NOT
    total_bank = db.Column(db.Integer, default=0)  # Общий банк (BONES + NOT)
    is_winner = db.Column(db.Boolean, default=False)  # Карточка-победитель

    def __init__(self, image_url, round_id):
        self.image_url = image_url
        self.round_id = round_id

    def __repr__(self):
        return f'<Card {self.text}>'

#  Модель ставок
class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Кто сделал ставку
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)  # На какую карточку была сделана ставка
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))  # Привязка к активному раунду
    amount = db.Column(db.Integer, nullable=False)  # Сумма ставки
    bet_type = db.Column(db.String(10), nullable=False)  # Тип ставки: 'NOT' или 'BONES'
    placed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# Модель для управления реферальными бонусами
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