from sqlalchemy import LargeBinary, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from datetime import datetime
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    password: Mapped[bytes] = mapped_column(LargeBinary)
    posts: Mapped[List["Posts"]] = relationship("Posts", back_populates="author")
    comments: Mapped[List["Comments"]] = relationship(
        "Comments", back_populates="author"
    )
    following_relations: Mapped[List["Friends"]] = relationship(
        "Friends", foreign_keys="[Friends.follower_id]", back_populates="follower"
    )
    follower_relations: Mapped[List["Friends"]] = relationship(
        "Friends", foreign_keys="[Friends.following_id]", back_populates="following"
    )
    sended_message: Mapped[List["Messages"]] = relationship(
        "Messages",
        foreign_keys="[Messages.sender_id]",
        back_populates="sender",
    )
    received_message: Mapped[List["Messages"]] = relationship(
        "Messages",
        foreign_keys="[Messages.recipient_id]",
        back_populates="recipient",
    )


class Posts(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    author: Mapped["Users"] = relationship("Users", back_populates="posts")
    comments: Mapped[List["Comments"]] = relationship("Comments", back_populates="post")


class Comments(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    author: Mapped["Users"] = relationship("Users", back_populates="comments")
    post: Mapped["Posts"] = relationship("Posts", back_populates="comments")


class Friends(Base):
    __tablename__ = "friends"
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    following_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    is_friends: Mapped[bool] = mapped_column(default=False)
    follower: Mapped["Users"] = relationship(
        "Users", foreign_keys=[follower_id], back_populates="following_relations"
    )
    following: Mapped["Users"] = relationship(
        "Users", foreign_keys=[following_id], back_populates="follower_relations"
    )


class Messages(Base):
    __tablename__ = "messages"
    content: Mapped[str] = mapped_column(nullable=False)
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    sender: Mapped["Users"] = relationship(
        "Users", foreign_keys=[sender_id], back_populates="sended_message"
    )
    recipient: Mapped["Users"] = relationship(
        "Users", foreign_keys=[recipient_id], back_populates="received_message"
    )
