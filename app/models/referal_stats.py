from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app.models import Base


class ReferralStats(Base):
    __tablename__ = 'referral_stats'

    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # Пригласивший пользователь
    referral_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # Приглашенный пользователь
    referral_bet_id = Column(Integer, ForeignKey('bet.id'), nullable=False)  # Ставка реферала
    admin_bonus = Column(Integer, nullable=False)  # Бонус, который получил администратор
    referrer_bonus = Column(Integer, nullable=False)  # Бонус, который получил пригласивший игрок

    # Явное указание на внешние ключи через строки
    referrer = relationship('User', foreign_keys='ReferralStats.referrer_id', lazy='selectin')
    referral = relationship('User', foreign_keys='ReferralStats.referral_id', lazy='selectin')
    referral_bet = relationship('Bet', foreign_keys='ReferralStats.referral_bet_id', lazy='selectin')

    def __repr__(self):
        return f'<ReferralStats Referrer {self.referrer_id} Referral {self.referral_id}>'
