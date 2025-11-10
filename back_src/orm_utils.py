import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from password_utils import hash_password
from model_table import Base, Users
from config import settings


engine = create_engine(
    url=settings.database.url_psycopg2,
    echo=True,
    pool_size=5,
    max_overflow=10,
)


session_factory = sessionmaker(engine, expire_on_commit=False)


def get_session():
    with session_factory() as session:
        yield session


def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logging.error(f"Failed to create database tables: {e}")
        raise


def delete_database():
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception as e:
        logging.error(f"Failed to create database tables: {e}")
        raise


def add_user(session: Session, new_user):
    session.add(new_user)
    session.commit()


def get_user_by_email(
    session: Session,
    email,
):
    return session.execute(
        select(Users).where(email == Users.email)
    ).scalar_one_or_none()


def get_user_by_id(
    session: Session,
    id,
):
    return session.execute(select(Users).where(id == Users.id)).scalar_one_or_none()


def create_user(
    email: str,
    password: str,
):
    return Users(email=email, password=hash_password(password))
