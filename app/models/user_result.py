from sqlalchemy import Column, Integer, ForeignKey, Float, String
from sqlalchemy.orm import relationship
from app.models import Base


class UsersResults(Base):
    __tablename__ = 'users_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    card_id = Column(Integer, ForeignKey('card.id'), nullable=False)
    round_id = Column(Integer, ForeignKey('round.id'), nullable=False)
    bet_amount = Column(Integer, nullable=False)
    bet_type = Column(String(10), nullable=False)  # Например, 'NOT' или 'BONES'
    won_amount = Column(Float, nullable=True)  # Сумма выигрыша пользователя, если есть
    coefficient = Column(Float, nullable=True)  # Коэффициент расчета выигрыша, если применимо

    # Связи с другими таблицами
    user = relationship('User', back_populates='users_results', lazy='selectin')
    card = relationship('Card', back_populates='users_results', lazy='selectin')
    round = relationship('Round', back_populates='users_results', lazy='selectin')
