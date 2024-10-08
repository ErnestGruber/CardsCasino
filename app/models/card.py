from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app.models import Base


class Card(Base):
    __tablename__ = 'card'

    id = Column(Integer, primary_key=True)
    image_url = Column(String(255), nullable=False)
    round_id = Column(Integer, ForeignKey('round.id'), nullable=False)
    total_bones = Column(Integer, default=0)
    total_not = Column(Integer, default=0)
    total_bank = Column(Integer, default=0)
    is_winner = Column(Boolean, default=False)
    percentage_of_bank = Column(Float, default=0.0)

    # Связь с таблицей Round
    round = relationship('Round', back_populates='cards', overlaps="cards,related_round")

    def __init__(self, image_url, round_id):
        super().__init__()
        self.image_url = image_url
        self.round_id = round_id

    def __repr__(self):
        return f'<Card {self.id} Round {self.round_id}>'
