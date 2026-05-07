import os

from pydantic_settings import BaseSettings

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10.0"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


class Settings(BaseSettings):
    DB_HOST: str
    DB_USER: str
    DB_NAME: str
    DB_PORT: int
    DB_PASS: str

    REDIS_HOST: str
    REDIS_PORT: int

    REQUEST_TIMEOUT: float
    DEBUG: bool

    @property
    def DATABASE_URL(self) -> str:  # noqa
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
