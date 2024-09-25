from _datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.models import Base


class CashoutRequest(Base):
    __tablename__ = 'cashout_requests'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    wallet_address = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    user = relationship('User', backref='cashout_requests')
