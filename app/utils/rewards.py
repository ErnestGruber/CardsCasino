from sqlalchemy.future import select
from sqlalchemy import update
from app.models import Card, RoundStats, Bet, User, ReferralStats, ReferralBonus
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import ReferralStatsService, CardService


# Подсчет статистики и запись в базу данных
async def calculate_winner_and_stats(round_id: int, db: AsyncSession):
    # Получаем все карточки активного раунда
    card_service = CardService(db)
    cards = await card_service.get_cards_by_round_id(round_id)

    total_bones = sum(card.total_bones for card in cards)
    total_not = sum(card.total_not for card in cards)
    total_bank = total_bones + total_not

    # Комиссия администратору 15%
    admin_fee = total_bank * 0.15
    bank_after_fee = total_bank - admin_fee

    # Выявляем карту-победителя с наибольшими ставками
    winner_card = max(cards, key=lambda card: card.total_bones + card.total_not)
    for card in cards:
        card_percentage = ((card.total_bones + card.total_not) / total_bank) * 100 if total_bank > 0 else 0
        card.percentage_of_bank = card_percentage
    await db.commit()
    if winner_card:
        winning_bones = winner_card.total_bones
        winning_not = winner_card.total_not

        bones_coefficient = min(bank_after_fee / winning_bones, 1.8) if winning_bones > 0 else 0
        not_coefficient = bank_after_fee / winning_not if winning_not > 0 else 0

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
        db.add(new_stats)
        await db.commit()

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

# Асинхронное распределение наград
async def distribute_rewards(round_id: int, db: AsyncSession):
    # Получаем статистику раунда
    result = await db.execute(select(RoundStats).filter_by(round_id=round_id))
    round_stats = result.scalars().first()
    if not round_stats:
        return "Статистика для этого раунда не найдена!"

    # Получаем карту-победителя
    result = await db.execute(select(Card).filter_by(id=round_stats.winner_card_id))
    winner_card = result.scalars().first()
    if not winner_card:
        return "Карта-победитель не найдена!"

    # Получаем администратора
    result = await db.execute(select(User).filter_by(is_admin=True))
    admin = result.scalars().first()
    if not admin:
        return "Администратор не найден!"

    # Получаем все ставки на победившую карту
    result = await db.execute(select(Bet).filter_by(card_id=winner_card.id, round_id=round_id))
    winning_bets = result.scalars().all()

    for bet in winning_bets:
        result = await db.execute(select(User).filter_by(id=bet.user_id))
        user = result.scalars().first()

        # Рассчитываем выигрыш в зависимости от типа ставки
        if bet.bet_type == "BONES":
            winnings = bet.amount * round_stats.bones_coefficient
            winnings = min(winnings, bet.amount * 1.8)  # Ограничение на коэффициент
            user.bones += winnings
            print(f"Пользователь {user.username} получил {winnings} BONES")
        elif bet.bet_type == "NOT":
            winnings = bet.amount * round_stats.not_coefficient
            user.not_tokens += winnings
            admin.not_tokens -= winnings  # Администратор платит выигрыш
            print(f"Пользователь {user.username} получил {winnings} NOT")

        # Сохраняем изменения
        db.add(user)

    db.add(admin)
    await db.commit()

    return "Награды успешно распределены!"

# Асинхронное распределение реферальных бонусов
async def process_referral_bonus(user, referrer, bet_amount, bet_type, bet_id, db: AsyncSession):

    resultAdmin = await db.execute(select(User).filter_by(is_admin=True))
    admin = resultAdmin.scalars().first()

    if bet_type == "NOT":
        if admin:
            referrer_bonus = bet_amount * 0.05  # 5% пригласившему в BONES
            referrer.bones += referrer_bonus  # Бонус в  для реферера
            print(
                f"Начислено {referrer_bonus} бонусных BONES пользователю {referrer.username} за ставку реферала {user.username}")
            # Запись информации в таблицу referral_stats
            referral_stats_service = ReferralStatsService(db)
            await referral_stats_service.create_referral_stats(
                referrer_id=referrer.id,
                referral_id=user.id,
                referral_bet_id=bet_id,  # Использование корректного идентификатора ставки
                referrer_bonus=referrer_bonus
            )

    await db.commit()


#получение ставок
async def update_card_percentages(round_id: int, db: AsyncSession):
    # Получаем все карточки раунда
    card_service = CardService(db)
    cards = await card_service.get_cards_by_round_id(round_id)

    # Рассчитываем общий банк
    total_bones = sum(card.total_bones for card in cards)
    total_not = sum(card.total_not for card in cards)
    total_bank = total_bones + total_not

    if total_bank > 0:
        # Для каждой карточки рассчитываем процент от общего банка
        for card in cards:
            card_percentage = ((card.total_bones + card.total_not) / total_bank) * 100
            card.percentage_of_bank = card_percentage
    else:
        # Если банк пуст, устанавливаем процент для всех карточек в 0
        for card in cards:
            card.percentage_of_bank = 0

    await db.commit()
