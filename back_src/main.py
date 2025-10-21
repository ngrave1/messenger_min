from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from config import settings
from fastapi import FastAPI, Depends, HTTPException, status, Cookie
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from jwt_utils import hash_password, encode_jwt, decode_jwt, check_password
import jwt
from user_models import UserSchema, Users, Base
import uuid
from fastapi.responses import JSONResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

engine = create_engine(
    url=settings.DATABASE_URL_psycopg2,
    echo=True,
    pool_size=5,
    max_overflow=10
)

session_factory = sessionmaker(engine,
    expire_on_commit=False)

def get_session():
    with session_factory() as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]



@app.post("/setup_database/")
def create_tables():
    Base.metadata.create_all(bind=engine)
    return({"return" : True})
@app.delete("/delet_database/")
def delete_database():
    Base.metadata.drop_all(bind=engine)
    return({"return" : True})

def valid_auth_user(
        credentials: UserSchema,
        session: SessionDep
):
    query = select(Users).where(Users.email == credentials.email)
    res = session.execute(query)
    result = res.scalar_one_or_none()
    if result == None:
        raise HTTPException(status_code=401, detail="invalid token")
    access = check_password(
        password=credentials.password,
        hashed_password=result.password
    )
    if access:
        return result
    else:
        raise HTTPException(status_code=403, detail="invalid token")

def generate_session_id():
    return uuid.uuid4().hex

Cookies : dict[str] = {}

def create_access_token(
        user : UserSchema,
):
    jwt_payload = {
        "sub" : str(user.id),
        "token_type" : "access_token",
        "email" : user.email,
        }
    return encode_jwt(payload=jwt_payload)

def create_refresh_token(
        user : UserSchema,
):
    jwt_payload = {
        "sub" : str(user.id),
        "token_type" : "refresh_token",
        }
    return encode_jwt(payload=jwt_payload, expire_min=(60*24*30))

@app.post("/login/")
def login(
    user: Users = Depends(valid_auth_user),
):
    token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    session_id = generate_session_id()
    Cookies[session_id] = {
        "access_token": token,
    }
    response = JSONResponse(
        content={
            "refresh_token" : refresh_token,
            "access_token": token,
            "token_type": "Bearer"
        }
    )
    response.set_cookie(
        key="access_token", 
        value=token
        )
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token
        )

    return response

@app.post("/register/")
def update_database(
    User : UserSchema,
    session : SessionDep
    ):

    existing_user = session.execute(
        select(Users).where(Users.email == User.email)
    ).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    new_user = Users(
        email = User.email,
        password = hash_password(User.password)
    )
    session.add(new_user)
    session.commit()
    return({"return" : "user added"})

def check_user(
        payload : dict,
        token_type : str,
        session : SessionDep
):
    if token_type == "access_token":
        query = select(Users).where(payload['email'] == Users.email)
    else:
        query = select(Users).where(payload['sub'] == Users.id)
    return session.execute(query).scalar_one_or_none()

@app.get("/Release_access_token/")
def Release_access_token(
    session : SessionDep,
    refresh_token : str
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
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=401, detail="Token release failed")

@app.get("/check_token/")
def check_access_token(
    session : SessionDep,
    access_token: str = Cookie(alias="access_token"),
    refresh_token : str = Cookie(alias="refresh_token"),
):
    try:
        payload = decode_jwt(access_token)
        result = check_user(payload=payload, token_type="access_token", session=session)
        if result and payload['token_type'] == "access_token":
            return {"result" : True}
    except:
        try:
            refreshed_token = Release_access_token(session, refresh_token)
            return refreshed_token
        except:
            raise HTTPException(status_code=401, detail="autorisation failed")
    


"""

@app.get("/user_by_id/{user_id}")
def get_by_id(user_id : int, session : SessionDep):
    user = session.get(Users, user_id) 
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"id": user.id, "email": user.email}


@app.get("/all_user/")
def get_by_id(session : SessionDep):
    query = select(Users)
    result = session.execute(query).scalars().all()
    return [{"id": user.id, "email": user.email} for user in result]

"""