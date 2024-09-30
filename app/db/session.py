from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


# URL базы данных
DATABASE_URL = "postgresql+asyncpg://postgres:2281337@77.221.152.67:5432/royal"


# Инициализация асинхронного движка
engine = create_async_engine(DATABASE_URL,
                            pool_size=50,  # Максимальное количество соединений
                            max_overflow=10,  # Дополнительные соединения, если пул переполнен
                            pool_recycle=60,
                            pool_pre_ping=True)

# Настройка фабрики сессий
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Зависимость для получения асинхронной сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()
