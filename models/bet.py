from flask_sqlalchemy import SQLAlchemy
import datetime

from . import db

class Bet(db.Model):
    __tablename__ = 'bet'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    amount = db.Column(db.Integer, nullable=False)
    bet_type = db.Column(db.String(10), nullable=False)
    placed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_referral_bet = db.Column(db.Boolean, default=False)