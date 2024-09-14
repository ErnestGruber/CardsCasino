from flask import Flask, render_template, session, redirect, url_for
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Временные мок-данные для тестирования
mock_user = {
    'username': 'TestUser',
    'not_tokens': 50,
    'bones': 100
}

mock_round = {
    'description': 'Предсказание будущего мира',
    'target': 'Самая популярная карточка'
}

mock_cards = [
    {'id': 1, 'image_path': 'images/cheif-kief.png', 'text': 'Описание карточки 1'},
    {'id': 2, 'image_path': 'images/cntrlc.png', 'text': 'Описание карточки 2'},
    {'id': 3, 'image_path': 'images/hizenberg.png', 'text': 'Описание карточки 3'}
]

@app.route('/')
def index():
    user = mock_user
    return render_template('pages/index.html', username=user['username'], not_tokens=user['not_tokens'], bones=user['bones'])

@app.route('/game')
def game():
    round = mock_round
    cards = mock_cards
    return render_template('pages/game.html', round=round, cards=cards)

@app.route('/choose_card/<int:card_id>', methods=['POST'])
def choose_card(card_id):
    return f"Вы выбрали карточку с ID {card_id}", 200

if __name__ == '__main__':
    app.run(debug=True)
