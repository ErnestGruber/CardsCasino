from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from .user import User
from app.models import Base


class ReferralBonus(Base):
    __tablename__ = 'referral_bonus'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    referred_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    bonus_bones = Column(Integer, default=0)

    referred_user = relationship('User', foreign_keys='ReferralBonus.referred_user_id', lazy='selectin')
    user = relationship('User', foreign_keys='ReferralBonus.user_id', lazy='selectin')

    def __repr__(self):
        return f'<ReferralBonus User {self.user_id} referred {self.referred_user_id} with bonus {self.bonus_bones}>'
