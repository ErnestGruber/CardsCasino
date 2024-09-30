from sqlalchemy import engine_from_config
from sqlalchemy import pool
from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
from app.models import Base  # Убедитесь, что импортировали модели
from config import Config

# Этот конфигурационный объект доступен в .ini файле
config = context.config

# Настройка логирования из файла конфигурации.
fileConfig(config.config_file_name)

# Укажите метаданные для миграций
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = Config.DATABASE_URL,
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(Config.DATABASE_URL, poolclass=pool.NullPool)  # Синхронный движок

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
