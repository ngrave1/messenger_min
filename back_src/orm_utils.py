import logging
from sqlalchemy import create_engine, select, desc, delete
from sqlalchemy.orm import sessionmaker, Session, selectinload, load_only
from password_utils import hash_password
from model_table import Base, Users, Posts, Comments, Friends, Messages
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


def session_add(session: Session, new_object):
    try:
        session.add(new_object)
        session.commit()
    except:
        session.rollback()


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


def get_post_by_id(
    session: Session,
    post_id: int,
):
    return session.execute(select(Posts).where(Posts.id == post_id)).scalar_one_or_none()


def get_comment_by_id(
    session: Session,
    comment_id: int,
):
    return session.execute(select(Comments).where(Comments.id == comment_id)).scalar_one_or_none()


def create_user(
    email: str,
    password: str,
):
    return Users(email=email, password=hash_password(password))

def create_post(
    title: str,
    content: str,
    author_id: str,
    
):
    return Posts(title=title, content=content, author_id=int(author_id))


def create_comment(
    title: str,
    content: str,
    author_id: str,
    post_id: int,
    parent_id: int,
    
):
    return Comments(title=title, content=content, author_id=int(author_id), post_id=post_id, parent_id=parent_id)


def create_follower_pair(
    session: Session,
    follower_id: int,
    following_id: int, 

):
    reverse_friendship = session.execute(
        select(Friends).where(
            Friends.follower_id == following_id,
            Friends.following_id == follower_id
        )
    ).scalar_one_or_none()
    is_friends = False
    if reverse_friendship:
        is_friends = True
        reverse_friendship.is_friends = True
        session.commit()
    return Friends(follower_id=follower_id, following_id=following_id, is_friends=is_friends)
    

def is_frendship_exist(
    session: Session,
    follower_id: int,
    following_id: int, 
):
    result = session.execute(select(Friends).where(Friends.follower_id == follower_id, Friends.following_id == following_id)).scalar_one_or_none()
    return result is not None
    

def check_frendship(
        session: Session,
        follower_id: int,
        following_id: int,
):
    if session.execute(select(Friends).where(Friends.follower_id == follower_id & Friends.following_id == following_id & Friends.is_friends == True)):
        return "friends"
    elif session.execute(select(Friends).where(Friends.follower_id == follower_id & Friends.following_id == following_id)):
        return "follower"
    else:
        return None


def get_posts_orm(
        session: Session,
        limit: int,
        offset: int,
):
    result = session.execute(select(Posts)
                             .order_by(desc(Posts.updated_at))
                             .limit(limit=limit)
                             .offset(offset=offset)
                             .options(selectinload(Posts.author))
                             ).scalars().all()
    return result


def get_comments_orm(
        session: Session,
        limit: int,
        offset: int,
        post_id: int
):
    query = (
        select(Comments)
        .where(Comments.post_id == post_id)
        .options(
            load_only(
                Comments.id,
                Comments.title,
                Comments.content,
                Comments.parent_id,
                Comments.created_at,
                Comments.updated_at,
            )
        )
        .order_by(desc(Comments.created_at))
        .limit(limit)
        .offset(offset)
    )
    
    return session.execute(query).scalars().all()


def get_all_following_by_user_id(
    session: Session,
    user_id: int,
    only_friends: bool = False
):

    user = session.execute(
        select(Users)
        .where(Users.id == user_id)
        .options(selectinload(Users.following_relations))
    ).scalar_one_or_none()
    
    if not user:
        return []
    
    following = []
    
    for friendship in user.following_relations:
        if only_friends:
            if friendship.is_friends:
                following.append({
                    "id": friendship.following.id,
                    "email": friendship.following.email,
                    "is_friends": friendship.is_friends,
                })
        else:
            following.append({
                    "id": friendship.following.id,
                    "email": friendship.following.email,
                    "is_friends": friendship.is_friends,
                })
    
    return following


def delete_friendship(
    session: Session,
    follower_id: int,
    following_id: int,
):
    try:
        session.execute(
            delete(Friends).where(
                Friends.follower_id == follower_id,
                Friends.following_id == following_id
            )
        )
        
        reverse_friendship_stmt = select(Friends).where(
            Friends.follower_id == following_id,
            Friends.following_id == follower_id
        )
        
        reverse_friendship = session.execute(reverse_friendship_stmt).scalar_one_or_none()

        if reverse_friendship:
            reverse_friendship.is_friends = False
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise

 
def create_message_orm(
        content: str,
        sender_id: int,
        recipient_id: int,
):
    return Messages(content=content, sender_id=sender_id, recipient_id=recipient_id)


def get_full_chat_by_user_id(
        session: Session,
        user_id: int, 
        other_user_id: int,
):
    result = session.execute(select(Messages).where(((Messages.sender_id == user_id) & (Messages.recipient_id == other_user_id)) 
                                                 | ((Messages.sender_id == other_user_id) & (Messages.recipient_id == user_id)))
                                                 .order_by(Messages.sender_id)).scalars().all()
    messages = []
    for message in result:
        messages.append({
            "content": message.content,
            "sender_id": message.sender_id,
            "recipient_id": message.recipient_id,
        })
    return messages