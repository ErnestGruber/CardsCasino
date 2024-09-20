from datetime import datetime

from models import db


class RoundStats(db.Model):
    __tablename__ = 'round_stats'

    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)  # Привязка к раунду
    total_bones = db.Column(db.Float, nullable=False)  # Общий BONES в раунде
    total_not = db.Column(db.Float, nullable=False)  # Общий NOT в раунде
    total_bank = db.Column(db.Float, nullable=False)  # Общий банк
    admin_fee = db.Column(db.Float, nullable=False)  # Комиссия администратора
    bones_coefficient = db.Column(db.Float, nullable=False)  # Коэффициент для BONES
    not_coefficient = db.Column(db.Float, nullable=False)  # Коэффициент для NOT
    winner_card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)  # ID победившей карточки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Время создания записи

    def __init__(self, round_id, total_bones, total_not, total_bank, admin_fee, bones_coefficient, not_coefficient, winner_card_id):
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