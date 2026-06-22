from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field
from pathlib import Path


class DatabaseSettings(BaseSettings):
    host: str = Field(default="localhost")
    port: int = Field(default=5438)
    user: str = Field(default="postgres")
    password: str = Field(default="1488")
    name: str = Field(default="postgres")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="db_", extra="ignore")

    @property
    def url_asyncpg(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def url_psycopg2(self):
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class AuthJWT(BaseModel):
    private_key_path: Path = Path("./certs/jwt-private.pem")
    public_key_path: Path = Path("./certs/jwt-public.pem")
    algorithm: str = "RS256"
    access_token_expire: int = 15
    refresh_token_expire: int = 30


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    auth_jwt: AuthJWT = AuthJWT()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
