from pydantic import BaseModel, EmailStr, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr
    password: str


class Access_Token(BaseModel):
    access_token: str
    token_type: str
