from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from . import Base


class Awards(Base):
    __tablename__ = 'awards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    rule_1 = Column(Boolean, default=False)
    rule_2 = Column(Boolean, default=False)
    rule_3 = Column(Boolean, default=False)
    rule_4 = Column(Boolean, default=False)
    rule_5 = Column(Boolean, default=False)

    user = relationship('User', backref='awards')
