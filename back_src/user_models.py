from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import LargeBinary, String

class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr
    password: str

class Access_Token(BaseModel):
    access_token: str
    token_type: str 


class Base(DeclarativeBase):
    pass



class Users(Base):
    __tablename__ = "autorisation"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    password: Mapped[bytes] = mapped_column(LargeBinary)