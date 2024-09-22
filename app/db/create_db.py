import asyncio

# Импортируем ваши модели
from app.models import Base  # Объедините все модели в `Base`
from session import engine  # Подключение к базе данных

# Инициализируем базу данных
async def init_db():
    async with engine.begin() as conn:
        # Создаем все таблицы в базе данных
        print("Создание таблиц в базе данных...")
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы успешно созданы!")

# Асинхронная функция для инициализации
async def main():
    await init_db()

# Запуск скрипта
if __name__ == "__main__":
    asyncio.run(main())