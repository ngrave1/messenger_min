from fastapi import FastAPI, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from model_table import Users
from user_models import UserSchema
from jwt_utils import create_access_token, Release_access_token, create_refresh_token, check_user, valid_auth_user, hash_password, decode_jwt, generate_session_id, Cookies
from orm_utils import custom_query_where, add_user, SessionDep


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/login/")
def login(
    user : Users = Depends(valid_auth_user),
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
    ):
    existing_user = custom_query_where(Users.email, User.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    new_user = Users(
        email = User.email,
        password = hash_password(User.password)
    )
    add_user(new_user)
    return({"return" : "user added"})


@app.get("/check_token/")
def check_access_token(
    access_token: str = Cookie(alias="access_token"),
    refresh_token : str = Cookie(alias="refresh_token"),
):
    try:
        print(access_token)
        payload = decode_jwt(access_token)
        print(payload)
        result = check_user(payload=payload, token_type="access_token")
        if result and payload['token_type'] == "access_token":
            return {"result" : True}
    except:
        try:
            refreshed_token = Release_access_token(refresh_token)
            return refreshed_token
        except:
            raise HTTPException(status_code=401, detail="autorisation failed")
    
