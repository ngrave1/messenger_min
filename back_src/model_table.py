from sqlalchemy import LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "authorization"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    password: Mapped[bytes] = mapped_column(LargeBinary)