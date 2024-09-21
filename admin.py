from flask_admin import Admin, BaseView, expose
from flask import request
from werkzeug.utils import secure_filename
from models import Round, Card, Bet, db, User, RoundStats
import os
from datetime import datetime

from services import calculate_winner_and_stats
from services.admin import admin_auth_required

# Инициализация админ-панели
admin = Admin()

class RoundAdminView(BaseView):
    @expose('/')
    @admin_auth_required  # Используем декоратор для защиты админки
    def index(self):
        return self.render('admin/round_form.html')  # Используем шаблон для создания раунда

    @expose('/create-round', methods=['GET', 'POST'])
    @admin_auth_required  # Защита создания раунда
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
            card1 = Card(image_url=os.path.join(upload_folder, filename1), round_id=new_round.id)
            card2 = Card(image_url=os.path.join(upload_folder, filename2), round_id=new_round.id)
            card3 = Card(image_url=os.path.join(upload_folder, filename3), round_id=new_round.id)

            db.session.add_all([card1, card2, card3])
            db.session.commit()

            return "Раунд успешно создан и активирован!"

        return self.render('admin/round_form.html')

class BetStatsView(BaseView):
    @expose('/')
    @admin_auth_required  # Защита статистики ставок
    def bets_stats(self):
        active_round = Round.query.filter_by(is_active=True).first()
        if not active_round:
            return "Нет активного раунда для отображения статистики."

        cards = Card.query.filter_by(round_id=active_round.id).all()
        total_bones = sum(card.total_bones for card in cards)
        total_not = sum(card.total_not for card in cards)
        total_bank = total_bones + total_not

        stats = []
        for card in cards:
            card_bank = card.total_bones + card.total_not
            percentage = (card_bank / total_bank) * 100 if total_bank > 0 else 0
            stats.append({
                'image_url': card.image_url,
                'total_bones': card.total_bones,
                'total_not': card.total_not,
                'percentage': round(percentage, 2)
            })

        results = calculate_winner_and_stats(active_round.id)
        return self.render('admin/bets_stats.html', stats=stats, total_bank=total_bank, results=results)

# Функция для инициализации админки
def setup_admin(app):
    from flask_admin import Admin
    admin = Admin(app, name="Админка", template_mode="bootstrap3")
    admin.add_view(RoundAdminView(name="Создать раунд"))
    admin.add_view(BetStatsView(name="Статистика ставок"))