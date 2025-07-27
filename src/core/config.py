# from pydantic import BaseSettings, PostgresDsn, RedisDsn
# from typing import Optional
from pydantic_settings import BaseSettings
#from pydantic import  PostgresDsn, RedisDsn

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI App"
    DEBUG: bool = True

    DATABASE_URL: str

    REDIS_URL: str 

    DEFAULT_SKIP: int = 0
    DEFAULT_LIMIT: int = 10
    MAX_LIMIT: int = 100

    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
