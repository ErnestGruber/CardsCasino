from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
# Инициализация базы данных
from .user import User
from .round import Round
from .card import Card
from .bet import Bet
from .referral_bonus import ReferralBonus
from .token import Token
from .round_stats import RoundStats
from .referal_stats import ReferralStats
from .deposit_request import DepositRequest
from .cashout_request import CashoutRequest
from .awards import Awards

__all__ = [
    'User',
    'Round',
    'Card',
    'Bet',
    'ReferralBonus',
    'Token',
    'RoundStats',
    'ReferralStats',
    'DepositRequest',
    'CashoutRequest'
]