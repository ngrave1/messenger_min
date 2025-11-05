from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from model_table import Users
from user_models import UserSchema
from jwt_utils import (
    create_access_token,
    release_access_token,
    create_refresh_token,
    check_user,
    valid_auth_user,
    hash_password,
    decode_jwt,
)
from orm_utils import add_user, get_user_by_email
from dependencies import SessionDep


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
    response.set_cookie(key="access_token", value=token)
    response.set_cookie(key="refresh_token", value=refresh_token)

    return response


@router.post("/register/")
def update_database(
    session: SessionDep,
    user: UserSchema,
):
    existing_user = get_user_by_email(session, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    new_user = Users(email=user.email, password=hash_password(user.password))
    add_user(session, new_user)
    return {"return": f"user added, id {user.email}"}


@router.patch("/check_token/")
def check_access_token(
    session: SessionDep,
    access_token: str = Cookie(alias="access_token"),
    refresh_token: str = Cookie(alias="refresh_token"),
):
    try:
        payload = decode_jwt(access_token)
        result = check_user(payload=payload, token_type="access_token", session=session)
        if result and payload["token_type"] == "access_token":
            return {"result": True}
    except:
        try:
            refreshed_token = release_access_token(refresh_token, session)
            return refreshed_token
        except:
            raise HTTPException(status_code=401, detail="authorization failed")
