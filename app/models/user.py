import secrets
import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, backref

from . import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    bones = Column(Integer, default=100)  # Баланс BONES
    not_tokens = Column(Integer, default=0)  # Баланс NOT токенов
    referral_code = Column(String(100), unique=True)  # Уникальный реферальный код
    referred_by = Column(String(100), ForeignKey('user.referral_code'), nullable=True)  # Реферал
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # Дата регистрации
    token = Column(String(60), unique=True, nullable=False)  # Токен
    is_admin = Column(Boolean, default=False)  # Администратор или нет
    wallet_address = Column(String(255), default="0xDefaultWallet")  # Адрес кошелька
    ip_address = Column(String(45), nullable=True)

    # Рефералы и пригласивший
    referrals = relationship('User', backref='referrer', remote_side=[referral_code])

    # Ставки пользователя
    bets = relationship('Bet', back_populates='user', overlaps="bets_from_user,bet_user")
    def __init__(self, id, username, token: str = None, bones=100, not_tokens=0, referral_code=None, referred_by=None, is_admin=False,
                 wallet_address="0xDefaultWallet"):
        super().__init__()
        self.id = id
        self.bones = bones
        self.not_tokens = not_tokens
        self.username = username
        self.referral_code = referral_code or secrets.token_hex(5)
        self.referred_by = referred_by
        self.is_admin = is_admin
        self.wallet_address = wallet_address
        self.token = token
