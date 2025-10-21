from config import settings
import jwt
import bcrypt
from datetime import datetime, timedelta

def encode_jwt(
        payload: dict,
        private_key: str = settings.authJWT.private_key_path.read_text(),
        algorithm: str = settings.authJWT.algorithm,
        expire_min: int = settings.authJWT.access_token_expire
):
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_min)
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