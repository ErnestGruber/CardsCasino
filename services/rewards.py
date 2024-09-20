from models import User, db, RoundStats, Card, Bet


def calculate_winner_and_stats(round_id):
    # Получаем все карточки активного раунда
    cards = Card.query.filter_by(round_id=round_id).all()

    total_bones = sum(card.total_bones for card in cards)
    total_not = sum(card.total_not for card in cards)
    total_bank = total_bones + total_not

    # Комиссия администратору 15%
    admin_fee = total_bank * 0.15
    bank_after_fee = total_bank - admin_fee

    # Выявляем карту-победителя с наибольшими ставками
    winner_card = max(cards, key=lambda card: card.total_bones + card.total_not)

    # Если у победителя есть BONES
    if winner_card:
        winning_bones = winner_card.total_bones
        winning_not = winner_card.total_not

        # Коэффициенты для победителей
        bones_coefficient = min(bank_after_fee / winning_bones, 1.8) if winning_bones > 0 else 0
        not_coefficient = (bank_after_fee / winning_not) if winning_not > 0 else 0

        # Сохраняем данные в таблицу RoundStats
        new_stats = RoundStats(
            round_id=round_id,
            total_bones=total_bones,
            total_not=total_not,
            total_bank=total_bank,
            admin_fee=admin_fee,
            bones_coefficient=bones_coefficient,
            not_coefficient=not_coefficient,
            winner_card_id=winner_card.id
        )
        db.session.add(new_stats)
        db.session.commit()

        return {
            "total_bones": total_bones,
            "total_not": total_not,
            "total_bank": total_bank,
            "admin_fee": admin_fee,
            "winner_card": winner_card,
            "bones_coefficient": bones_coefficient,
            "not_coefficient": not_coefficient
        }
    else:
        return {"error": "Нет победителя в этом раунде"}
# подсчет наград из таблицы (раунд должен быть завершен - добавить в конце)
def distribute_rewards(round_id):
    # Получаем статистику раунда
    round_stats = RoundStats.query.filter_by(round_id=round_id).first()
    if not round_stats:
        return "Статистика для этого раунда не найдена!"

    # Получаем карту-победителя
    winner_card = Card.query.filter_by(id=round_stats.winner_card_id).first()
    if not winner_card:
        return "Карта-победитель не найдена!"

    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        return "Администратор не найден!"

    # Получаем все ставки на победившую карту
    winning_bets = Bet.query.filter_by(card_id=winner_card.id, round_id=round_id).all()

    for bet in winning_bets:
        user = User.query.get(bet.user_id)

        # Рассчитываем выигрыш в зависимости от типа ставки
        if bet.bet_type == "bones":
            # Вычисляем выигрыш для ставок BONES
            winnings = bet.amount * round_stats.bones_coefficient
            # Учитываем ограничение на коэффициент
            if round_stats.bones_coefficient > 1.8:
                winnings = bet.amount * 1.8

            # Добавляем выигрыш пользователю
            user.bones += winnings
            print(f"Пользователь {user.username} получил {winnings} BONES")

        elif bet.bet_type == "not_tokens":
            # Вычисляем выигрыш для ставок NOT
            winnings = bet.amount * round_stats.not_coefficient

            # Добавляем выигрыш пользователю
            # Обновляем баланс пользователя и админа для NOT
            user.not_tokens += winnings
            admin = User.query.filter_by(is_admin=True).first()
            if admin.not_tokens >= winnings:
                admin.not_tokens -= winnings
                print(f"Пользователь {user.username} получил {winnings} NOT")

        # Сохраняем изменения в базе данных
        db.session.add(user)

    # Обновляем баланс администратора
    db.session.add(admin)
    db.session.commit()

    return "Награды успешно распределены!"

def process_referral_bonus(user, referrer, bet_amount, bet_type):
    # Рассчитываем бонусы
    admin_bonus = bet_amount * 0.10  # 10% админу
    referrer_bonus = bet_amount * 0.05  # 5% пригласившему

    if bet_type == "not_tokens":
        referrer.bonus_not_tokens += referrer_bonus  # Бонус в NOT для реферера
        print(f"Начислено {referrer_bonus} бонусных NOT токенов пользователю {referrer.username} за ставку реферала {user.username}")
    else:
        referrer.bones += referrer_bonus  # Бонус в BONES
        print(f"Начислено {referrer_bonus} бонусных BONES пользователю {referrer.username} за ставку реферала {user.username}")

    # Обновляем администратора
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        admin.not_tokens += admin_bonus  # Администратору начисляются 10% в NOT
        print(f"Админу начислено {admin_bonus} NOT токенов")

    # Сохраняем изменения
    db.session.add(admin)
    db.session.add(referrer)

