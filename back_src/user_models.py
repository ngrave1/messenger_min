from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr
    password: str


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class CommentADDSchema(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    post_id: int = Field(gt=0)
    parent_id: int | None = None
    author_token: str
    

class PostADDSchema(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    author_token: str


class UserDTOSchema(BaseModel):
    id: int
    email: str
    

class PostDTOSchema(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime
    author: UserDTOSchema


class CommentDTOSchema(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    parent_id: int | None


class FollowerADDSchema(BaseModel):
    follower_id: int
    following_id: int


class FrendshipDTO(BaseModel):
    type: str | None


class FriendsSchema(FollowerADDSchema):
    is_friends: bool


class FriendDTOSchema(BaseModel):
    id: int
    email: str
    is_friends: bool


class MessageADDSchema(BaseModel):
    content: str
    sender_id: int
    recipient_id: int

    