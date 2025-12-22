import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

DB_HOST = os.getenv("db_host", "localhost")
DB_PORT = os.getenv("db_port", "5438")
DB_USER = os.getenv("db_user", "postgres")
DB_PASSWORD = os.getenv("db_password", "1488")
DB_NAME = os.getenv("db_name", "postgres")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"