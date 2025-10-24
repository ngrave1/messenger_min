from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session 
from fastapi import Depends
from typing import Annotated
from model_table import Base, Users
from config import settings


engine = create_engine(
    url=settings.DATABASE_URL_psycopg2,
    echo=True,
    pool_size=5,
    max_overflow=10
)


session_factory = sessionmaker(engine,
    expire_on_commit=False)


def get_session():
    with session_factory() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_tables():
    Base.metadata.create_all(bind=engine)
    return({"return" : True})
def delete_database():
    Base.metadata.drop_all(bind=engine)
    return({"return" : True})


def add_user(
        NewUser,
): 
    with session_factory() as session:
        session.add(NewUser)
        session.commit()


def custom_query_where(
        FirstArg,
        SecondArg,
        table : Base = Users,
):
    with session_factory() as session:
        result = session.execute(select(table).where(FirstArg == SecondArg)).scalar_one_or_none()
        return result