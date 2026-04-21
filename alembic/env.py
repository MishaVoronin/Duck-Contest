import asyncio
import os
from logging.config import fileConfig
from pathlib import Path
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 🔹 Добавляем корень проекта в sys.path (чтобы работали абсолютные импорты)
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

# 🔹 Загружаем .env, если используется
from dotenv import load_dotenv
load_dotenv()

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 🔹 ИМПОРТИРУЕМ БАЗУ И ВСЕ МОДЕЛИ!
# Без этого Alembic не увидит таблицы при autogenerate
from database.db import Base
# from models import User, Product, Order  # ← раскомментируйте и добавьте свои

target_metadata = Base.metadata

def get_url():
    # Берёт URL из .env или alembic.ini (если не закомментировано)
    return os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

def run_migrations_offline() -> None:
    """Запуск миграций без подключения к БД (генерация SQL)"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Асинхронный запуск миграций"""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Важно для CLI: не держит пул между миграциями
    )
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    """Точка входа для online-миграций"""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()