from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path

class AuthJWT(BaseModel):
    private_key_path : Path = Path("./certs/jwt-privat.pem")
    public_key_path : Path = Path("./certs/jwt-public.pem")
    algorithm: str = "RS256"
    access_token_expire: int = 1
    
class Settings(BaseSettings):
    DB_HOST : str
    DB_PORT : int
    DB_USER : str
    DB_PASS : int
    DB_NAME : str


    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_URL_psycopg2(self): 
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file=".env")

    authJWT: AuthJWT = AuthJWT()



settings = Settings()