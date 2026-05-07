"""Database connection utilites for PostgreSQL"""
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import settings

async def get_pool() -> asyncpg.Pool:
    """Create and return pool"""
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME', 'postgres')

    # Валидация
    if not user:
        raise ValueError('DB_USER must be set in .env')
    if not password:
        raise ValueError('DB_PASSWORD must be set in .env')
    
    # Создаём пул соединений
    pool = await asyncpg.create_pool(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        min_size=1,      # минимум 1 соединение в пуле
        max_size=10,     # максимум 10 соединений
    )
    return pool    

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)