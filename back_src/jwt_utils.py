import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from orm_utils import get_user_by_email, get_user_by_id
from user_models import UserSchema
from config import settings
from dependencies import SessionDep


Cookies : dict[str] = {}


def generate_session_id():
    return uuid.uuid4().hex


def encode_jwt(
        payload: dict,
        token_type: str,
        private_key: str = settings.authJWT.private_key_path.read_text(),
        algorithm: str = settings.authJWT.algorithm,
):
    if token_type == "access_token":
        expire_time = timedelta(minutes=settings.authJWT.access_token_expire)
    else:
        expire_time = timedelta(days=settings.authJWT.refresh_token_expire)
    now = datetime.utcnow()
    expire = now + expire_time
    payload_exp = payload.copy()
    payload_exp.update(
        exp=expire,
    )
    encoded = jwt.encode(
        payload_exp,
        private_key,
        algorithm=algorithm
    )
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = settings.authJWT.public_key_path.read_text(),
        algorithm: str = settings.authJWT.algorithm
):
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )
    return decoded


def hash_password(
     password: str
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)

def check_password(
        password: str,
        hashed_password: bytes
) -> bool: 
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password
    )


def valid_auth_user(
        credentials: UserSchema,
        session: SessionDep
):
    result = get_user_by_email(credentials.email, session)
    if result == None:
        raise HTTPException(status_code=401, detail="invalid token")
    access = check_password(
        password=credentials.password,
        hashed_password=result.password
    )
    if access:
        return result
    raise HTTPException(status_code=403, detail="invalid token")
 

def create_access_token(
        user: UserSchema,
):
    jwt_payload = {
        "sub": str(user.id),
        "token_type": "access_token",
        "email": user.email,
        }
    return encode_jwt(payload=jwt_payload, token_type="access_token")

def create_refresh_token(
        user: UserSchema,
): 
    jwt_payload = {
        "sub": str(user.id),
        "token_type": "refresh_token",
        }
    return encode_jwt(payload=jwt_payload, token_type="refresh_token")


def check_user(
        payload: dict,
        token_type: str,
        session: Session
):
    if token_type == "access_token":
        result = get_user_by_email(payload['email'], session)
    else:
        result = get_user_by_id(payload['sub'], session)
    return result


def release_access_token(
    refresh_token: str,
    session: Session,
): 
    try:
        payload = decode_jwt(refresh_token)
        result = check_user(payload=payload, token_type="refresh_token", session=session)
        if result and payload['token_type'] == "refresh_token":
            user = result
            token = create_access_token(user)
            session_id = generate_session_id()
            Cookies[session_id] = {
                "access_token": token,
            }
            response = JSONResponse(
                content={
                "access_token": token,
                }
            )
            response.set_cookie(
            key="access_token", 
            value=token
            )
            return response
    except:
        raise HTTPException(status_code=401, detail="Token release failed")
