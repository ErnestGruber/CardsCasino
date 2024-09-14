from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from cards_casino.infrastructure.database.models import db, User, Card, Round

def setup_admin(app):
    admin = Admin(app, name='Game Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Card, db.session))
    admin.add_view(ModelView(Round, db.session))