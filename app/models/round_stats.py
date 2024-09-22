from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models import Base


class RoundStats(Base):
    __tablename__ = 'round_stats'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('round.id'), nullable=False)  # Привязка к раунду
    total_bones = Column(Float, nullable=False)  # Общий BONES в раунде
    total_not = Column(Float, nullable=False)  # Общий NOT в раунде
    total_bank = Column(Float, nullable=False)  # Общий банк
    admin_fee = Column(Float, nullable=False)  # Комиссия администратора
    bones_coefficient = Column(Float, nullable=False)  # Коэффициент для BONES
    not_coefficient = Column(Float, nullable=False)  # Коэффициент для NOT
    winner_card_id = Column(Integer, ForeignKey('card.id'), nullable=False)  # ID победившей карточки
    created_at = Column(DateTime, default=datetime.utcnow)  # Время создания записи

    # Связь с другими таблицами
    round = relationship("Round", backref="round_stats", lazy="selectin")
    winner_card = relationship("Card", backref="won_rounds", lazy="selectin")

    def __init__(self, round_id, total_bones, total_not, total_bank, admin_fee, bones_coefficient, not_coefficient,
                 winner_card_id):
        super().__init__()
        self.round_id = round_id
        self.total_bones = total_bones
        self.total_not = total_not
        self.total_bank = total_bank
        self.admin_fee = admin_fee
        self.bones_coefficient = bones_coefficient
        self.not_coefficient = not_coefficient
        self.winner_card_id = winner_card_id

    def __repr__(self):
        return f'<RoundStats Round {self.round_id}>'
