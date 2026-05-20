from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Вычисляем корень проекта Sentinel (два уровня вверх от config.py)
SENTINEL_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(SENTINEL_ROOT / ".env"),
        env_file_encoding="utf-8",
    )
    DB_HOST: str
    DB_USER: str
    DB_NAME: str
    DB_PORT: int = 5432
    DB_PASS: str

    REDIS_HOST: str
    REDIS_PORT: int = 6379

    MINIO_USER: str
    MINIO_PASS: str
    MINIO_HOST: str
    MINIO_PORT: int

    GF_USER: str
    GF_PASS: str

    REQUEST_TIMEOUT: float
    DEBUG: bool

    @property
    def DATABASE_URL(self) -> str:  # noqa
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
