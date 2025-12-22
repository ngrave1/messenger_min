# env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from pathlib import Path
import sys
import os

# Добавляем родительскую директорию в путь
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Загружаем .env файл если он есть
env_path = parent_dir / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print(f"Loaded .env from: {env_path}")
    except ImportError:
        print("python-dotenv not installed, using environment variables")

db_host = os.getenv("db_host", "localhost")
db_port = os.getenv("db_port", "5438")
db_user = os.getenv("db_user", "postgres")
db_password = os.getenv("db_password", "1488")
db_name = os.getenv("db_name", "postgres")

DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

print(f"Using database URL: {DATABASE_URL}")

from model_table import *
from model_table import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", DATABASE_URL)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()