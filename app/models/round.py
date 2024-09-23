from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.models import Base


class Round(Base):
    __tablename__ = 'round'

    id = Column(Integer, primary_key=True)
    description = Column(String(255), nullable=False)
    target = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False)

    cards = relationship('Card', back_populates='round', overlaps="round,cards_in_round")

    def __init__(self, description, target, start_time, end_time, is_active=False):
        super().__init__()
        self.description = description
        self.target = target
        self.start_time = start_time
        self.end_time = end_time
        self.is_active = is_active

    def __repr__(self):
        return f'<Round {self.description}>'
