import os
from flask import request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from models import Round, Card, db

UPLOAD_FOLDER = 'static/images/cards/'  # Папка для загрузки изображений
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin/create-round', methods=['GET', 'POST'])
def create_round():
    if request.method == 'POST':
        # Получаем данные формы
        description = request.form['description']
        target = request.form['target']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        # Получаем загруженные файлы
        card1_image = request.files['card1_image']
        card2_image = request.files['card2_image']
        card3_image = request.files['card3_image']

        # Проверяем и сохраняем изображения
        if card1_image and allowed_file(card1_image.filename):
            filename1 = secure_filename(card1_image.filename)
            card1_image.save(os.path.join(UPLOAD_FOLDER, filename1))

        if card2_image and allowed_file(card2_image.filename):
            filename2 = secure_filename(card2_image.filename)
            card2_image.save(os.path.join(UPLOAD_FOLDER, filename2))

        if card3_image and allowed_file(card3_image.filename):
            filename3 = secure_filename(card3_image.filename)
            card3_image.save(os.path.join(UPLOAD_FOLDER, filename3))

        # Сохраняем раунд и карточки в базу данных
        round = Round(description=description, target=target, start_time=start_time, end_time=end_time)
        db.session.add(round)
        db.session.commit()

        # Создаем карточки
        card1 = Card(text=request.form['card1_text'], image_url=os.path.join(UPLOAD_FOLDER, filename1), round=round)
        card2 = Card(text=request.form['card2_text'], image_url=os.path.join(UPLOAD_FOLDER, filename2), round=round)
        card3 = Card(text=request.form['card3_text'], image_url=os.path.join(UPLOAD_FOLDER, filename3), round=round)

        # Сохраняем карточки
        db.session.add_all([card1, card2, card3])
        db.session.commit()

        flash('Раунд успешно создан!')
        return redirect(url_for('admin.index'))

    return render_template('round_form.html')
