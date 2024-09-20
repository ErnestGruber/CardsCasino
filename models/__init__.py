from flask_sqlalchemy import SQLAlchemy

# Инициализация базы данных
db = SQLAlchemy()
from .user import User
from .round import Round
from .card import Card
from .bet import Bet
from .referral_bonus import ReferralBonus
from .token import Token
from .round_stats import RoundStats