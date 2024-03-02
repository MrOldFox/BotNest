from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine  # Импортируем create_engine
from alembic import context
from core.database.models import Base  # Путь к вашему Base может отличаться


# Импортируем метаданные моделей
target_metadata = Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_online():
    """Run migrations in 'online' mode with a connection to the database."""
    # Используем create_engine для создания подключения
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Дополнительные параметры могут быть добавлены здесь
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()