from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
# Инициализация базы данных
db = SQLAlchemy()
from .user import User
from .round import Round
from .card import Card
from .bet import Bet
from .referral_bonus import ReferralBonus
from .token import Token
from .round_stats import RoundStats
from .referal_stats import ReferralStats