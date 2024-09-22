from quart import Quart
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import User

app = Quart(__name__)

# Создание асинхронного движка базы данных
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"  # Пример для PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание фабрики сессий для асинхронных запросов
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Использование сессии в приложении Quart
@app.before_serving
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.after_serving
async def close_db():
    await engine.dispose()

@app.route('/')
async def index():
    async with async_session() as session:
        # Ваши асинхронные запросы к базе данных
        result = await session.execute(select(User).where(User.id == 1))
        user = result.scalar()
        return f"Hello, {user.username}"

if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config as HyperConfig

    config = HyperConfig()
    config.bind = ["127.0.0.1:5000"]
    asyncio.run(serve(app, config))

# # После того, как приложение создано и инициализировано, импортируем setup_admin
# from admin import setup_admin
#
# # Запуск админки после инициализации приложения
# setup_admin(app)
# async def create_app():
#     async with app.app_context():
#         await db.create_all()  # Создаем таблицы при запуске приложения
#     config = HyperConfig()
#     config.bind = ["127.0.0.1:5000"]
#     await serve(app, config)
# # Запуск приложения
# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(create_app())

