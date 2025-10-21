from sqlalchemy.orm import Mapped, mapped_column
from back_src.main import Base


class Workers(Base):
    __tablename__ = "workertable"

    id : Mapped[int] = mapped_column(primary_key=True)
    username : Mapped[str]