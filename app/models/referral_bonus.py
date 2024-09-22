from . import db
class ReferralBonus(db.Model):
    __tablename__ = 'referral_bonus'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bonus_bones = db.Column(db.Integer, default=0)

    referred_user = db.relationship('User', foreign_keys=[referred_user_id])
    user = db.relationship('User', foreign_keys=[user_id])