from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from model_table import Users
from user_models import (
    UserSchema,
    UserDTOSchema,
    PostADDSchema,
    CommentADDSchema,
    TokensSchema,
    PostDTOSchema,
    CommentDTOSchema,
    FollowerADDSchema,
    FriendDTOSchema,
    MessageADDSchema,
    PostDeleteSchema,
    CommentDeleteSchema,
)
from jwt_utils import (
    create_access_token,
    create_refresh_token,
    valid_auth_user,
    decode_jwt,
    sub_check_access_token,
)
from orm_utils import (
    session_add,
    get_user_by_email,
    create_user,
    create_post,
    create_comment,
    get_post_by_id,
    get_posts_orm,
    get_comments_orm,
    is_frendship_exist,
    create_follower_pair,
    get_all_following_by_user_id,
    delete_friendship_orm,
    create_message_orm,
    get_full_chat_by_user_id,
    delete_user_orm,
    delete_post_orm,
    delete_comment_orm,
)
from dependencies import SessionDep
from typing import List
import logging


router = APIRouter()


@router.post("/login/")
def login(
    user: Users = Depends(valid_auth_user),
):
    token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    response = JSONResponse(
        content={
            "refresh_token": refresh_token,
            "access_token": token,
            "token_type": "Bearer",
        }
    )
    return response


@router.post("/register/")
def update_users(
    session: SessionDep,
    user: UserSchema,
):
    existing_user = get_user_by_email(session, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    new_user = create_user(user.email, user.password)
    session_add(session, new_user)
    return {"return": f"user added, id {user.email}"}


@router.delete("/delete_user")
def delete_user(
    session: SessionDep,
    user: UserDTOSchema,
):
    try:
        delete_user_orm(session=session, user_id=user.id)
    except:
        raise HTTPException(status_code=404, detail="User does not exist")


@router.patch("/check_token/")
def check_access_token(
    session: SessionDep,
    tokens: TokensSchema,
):
    access_token = tokens.access_token
    refresh_token = tokens.refresh_token
    return sub_check_access_token(
        session=session, access_token=access_token, refresh_token=refresh_token
    )


@router.post("/update_posts/")
def update_posts(
    session: SessionDep,
    payload: PostADDSchema,
):
    try:
        decoded_token = decode_jwt(payload.author_token)
        new_post = create_post(
            title=payload.title, content=payload.content, author_id=decoded_token["sub"]
        )
        session_add(session, new_post)
        return {"result": f"post {payload.title} added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Post isn`t publicated")


@router.post("/update_comments/")
def update_comments(
    session: SessionDep,
    payload: CommentADDSchema,
):
    try:
        if get_post_by_id(session=session, post_id=payload.post_id):
            decoded_token = decode_jwt(payload.author_token)
            new_comment = create_comment(
                title=payload.title,
                content=payload.content,
                author_id=decoded_token["sub"],
                post_id=payload.post_id,
                parent_id=payload.parent_id,
            )
            session_add(session, new_comment)
            return {"result": f"comment {payload.title} added"}
        else:
            raise HTTPException(status_code=404, detail="Invalid post id")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Comment isn`t publicated")


@router.get("/get_posts/", response_model=List[PostDTOSchema])
def get_posts(
    session: SessionDep,
    limit: int = 20,
    offset: int = 0,
):
    posts = get_posts_orm(session=session, limit=limit, offset=offset)
    result = [PostDTOSchema.model_validate(row, from_attributes=True) for row in posts]
    return result


@router.delete("/delete_post/")
def delete_post(
    session: SessionDep,
    post: PostDeleteSchema,
):
    try:
        delete_post_orm(session=session, post_id=post.post_id)
    except:
        raise HTTPException(status_code=404, detail="Post does not exist")


@router.get("/get_comments/", response_model=List[CommentDTOSchema])
def get_comments(
    session: SessionDep,
    post_id: int,
    limit: int = 20,
    offset: int = 0,
):
    comments = get_comments_orm(
        session=session, limit=limit, offset=offset, post_id=post_id
    )
    result = [
        CommentDTOSchema.model_validate(row, from_attributes=True) for row in comments
    ]
    return result


@router.delete("/delete_comment/")
def delete_post(
    session: SessionDep,
    comment: CommentDeleteSchema,
):
    try:
        delete_comment_orm(session=session, comment_id=comment.comment_id)
    except:
        raise HTTPException(status_code=404, detail="Comment does not exist")


@router.post("/update_followers/")
def update_followers(
    session: SessionDep,
    payload: FollowerADDSchema,
):
    if is_frendship_exist(session, payload.follower_id, payload.following_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Pair already exists"
        )
    new_pair = create_follower_pair(
        session=session,
        follower_id=payload.follower_id,
        following_id=payload.following_id,
    )
    session_add(session=session, new_object=new_pair)
    return new_pair


@router.get("/get_friends/")
def get_friends(
    session: SessionDep,
    follower_id: int,
):
    try:
        friends = get_all_following_by_user_id(session=session, user_id=follower_id)
        result = [
            FriendDTOSchema.model_validate(row, from_attributes=True) for row in friends
        ]
        return result
    except Exception as e:
        logging.error(f"failed to get friends: {e}")
        raise


@router.delete("/delete_friend/")
def delete_friend(
    session: SessionDep,
    payload: FollowerADDSchema,
):
    try:
        delete_friendship_orm(
            session=session,
            follower_id=payload.follower_id,
            following_id=payload.following_id,
        )
        return {"result": "friendship deleted"}
    except:
        raise HTTPException(status_code=400, detail="can`t delet friendship")


@router.post("/send_message/")
def create_message(
    session: SessionDep,
    payload: MessageADDSchema,
):
    new_message = create_message_orm(
        content=payload.content,
        sender_id=payload.sender_id,
        recipient_id=payload.recipient_id,
    )
    session_add(session=session, new_object=new_message)


@router.get("/get_chat/")
def get_chat(
    session: SessionDep,
    user_id: int,
    other_user_id: int,
):
    chat = get_full_chat_by_user_id(
        session=session, user_id=user_id, other_user_id=other_user_id
    )
    return [MessageADDSchema.model_validate(row) for row in chat]
