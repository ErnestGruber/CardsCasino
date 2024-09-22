from . import db

class Card(db.Model):
    __tablename__ = 'card'

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)
    total_bones = db.Column(db.Integer, default=0)
    total_not = db.Column(db.Integer, default=0)
    total_bank = db.Column(db.Integer, default=0)
    is_winner = db.Column(db.Boolean, default=False)

    def __init__(self, image_url, round_id):
        self.image_url = image_url
        self.round_id = round_id
