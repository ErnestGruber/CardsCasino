from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base

class Bet(Base):
    __tablename__ = 'bet'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    card_id = Column(Integer, ForeignKey('card.id'), nullable=False)
    round_id = Column(Integer, ForeignKey('round.id'), nullable=True)
    amount = Column(Integer, nullable=False)
    bet_type = Column(String(10), nullable=False)
    placed_at = Column(DateTime, default=datetime.utcnow)
    is_referral_bet = Column(Boolean, default=False)

    # Связи с другими таблицами
    user = relationship('User', back_populates='bets', overlaps="bets_from_user,bet_user")
    card = relationship('Card', backref='bets_on_card', lazy='selectin')
    round = relationship('Round', backref='bets_in_round', lazy='selectin')
    # Добавляем ограничение на значения bet_type
    __table_args__ = (
        CheckConstraint(bet_type.in_(['NOT', 'BONES']), name='check_bet_type'),
    )

    def __init__(self, user_id, card_id, amount, bet_type, round_id=None, is_referral_bet=False):
        super().__init__()
        self.user_id = user_id
        self.card_id = card_id
        self.amount = amount
        self.bet_type = bet_type
        self.round_id = round_id
        self.is_referral_bet = is_referral_bet

    def __repr__(self):
        return f'<Bet User {self.user_id} Card {self.card_id} Amount {self.amount}>'
