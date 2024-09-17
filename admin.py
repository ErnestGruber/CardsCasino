from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask import render_template, request
from werkzeug.utils import secure_filename
from models import Round, Card, Bet, db
import os
from datetime import datetime

# Инициализация админ-панели
admin = Admin()

class RoundAdminView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/round_form.html')  # Используем шаблон для создания раунда

    @expose('/create-round', methods=['GET', 'POST'])
    def create_round(self):
        if request.method == 'POST':
            description = request.form['description']
            target = request.form['target']
            start_time = datetime.strptime(request.form['start_time'], "%Y-%m-%dT%H:%M")
            end_time = datetime.strptime(request.form['end_time'], "%Y-%m-%dT%H:%M")

            # Деактивируем все текущие раунды
            Round.query.update({'is_active': False})
            db.session.commit()

            # Создаем новый активный раунд
            new_round = Round(description=description, target=target, start_time=start_time, end_time=end_time, is_active=True)
            db.session.add(new_round)
            db.session.commit()

            # Проверка наличия папки для загрузки файлов
            upload_folder = 'static/uploads/'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)  # Создаем папку, если её нет

            # Обработка и сохранение изображений для карточек
            card1_image = request.files['card1_image']
            filename1 = secure_filename(card1_image.filename)
            card1_image.save(os.path.join(upload_folder, filename1))

            card2_image = request.files['card2_image']
            filename2 = secure_filename(card2_image.filename)
            card2_image.save(os.path.join(upload_folder, filename2))

            card3_image = request.files['card3_image']
            filename3 = secure_filename(card3_image.filename)
            card3_image.save(os.path.join(upload_folder, filename3))

            # Создаем карточки и добавляем их в базу данных
            card1 = Card(image_url=os.path.join(upload_folder, filename1), text=request.form['card1_text'], round_id=new_round.id)
            card2 = Card(image_url=os.path.join(upload_folder, filename2), text=request.form['card2_text'], round_id=new_round.id)
            card3 = Card(image_url=os.path.join(upload_folder, filename3), text=request.form['card3_text'], round_id=new_round.id)

            db.session.add_all([card1, card2, card3])
            db.session.commit()

            return "Раунд успешно создан и активирован!"

        return self.render('admin/round_form.html')

class BetStatsView(BaseView):
    @expose('/')
    def bets_stats(self):
        active_round = Round.query.filter_by(is_active=True).first()
        if not active_round:
            return "Нет активного раунда для отображения статистики."

        total_bets = db.session.query(db.func.count(Bet.id)).filter(Bet.round_id == active_round.id).scalar()
        cards = db.session.query(Card.text, db.func.count(Bet.id).label('total')).join(Bet).filter(Bet.round_id == active_round.id).group_by(Card.id).all()

        stats = []
        for card, count in cards:
            percentage = (count / total_bets) * 100 if total_bets > 0 else 0
            stats.append({
                'card': card,
                'count': count,
                'percentage': round(percentage, 2)
            })

        return self.render('admin/bets_stats.html', stats=stats, total_bets=total_bets)

def setup_admin(app):
    admin.init_app(app)
    admin.add_view(RoundAdminView(name="Создать раунд"))
    admin.add_view(BetStatsView(name="Статистика ставок"))
