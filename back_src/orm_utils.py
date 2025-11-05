from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from model_table import Base, Users
from config import settings


engine = create_engine(
    url=settings.DataBaseSettings.DATABASE_URL_psycopg2,
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
        print(e)


def delete_database():
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception as e:
        print(e)


def add_user(session: Session, new_user):
    session.add(new_user)
    session.commit()


def get_user_by_email(
    session: Session,
    email,
    table: Base = Users,
):
    return session.execute(
        select(table).where(email == Users.email)
    ).scalar_one_or_none()


def get_user_by_id(
    session: Session,
    id,
    table: Base = Users,
):
    return session.execute(select(table).where(id == Users.id)).scalar_one_or_none()
