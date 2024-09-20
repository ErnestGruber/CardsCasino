from flask_sqlalchemy import SQLAlchemy

from . import db

class Round(db.Model):
    __tablename__ = 'round'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    target = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    cards = db.relationship('Card', backref='round', lazy=True)

    def __init__(self, description, target, start_time, end_time, is_active=False):
        self.description = description
        self.target = target
        self.start_time = start_time
        self.end_time = end_time
        self.is_active = is_active