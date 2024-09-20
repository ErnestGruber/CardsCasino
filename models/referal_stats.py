from models import db


class ReferralStats(db.Model):
    __tablename__ = 'referral_stats'

    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Пригласивший пользователь
    referral_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Приглашенный пользователь
    referral_bet_id = db.Column(db.Integer, db.ForeignKey('bet.id'), nullable=False)  # Ставка реферала
    admin_bonus = db.Column(db.Integer, nullable=False)  # Бонус, который получил администратор
    referrer_bonus = db.Column(db.Integer, nullable=False)  # Бонус, который получил пригласивший игрок