import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings
from models import Base, Book

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_book(title: str, price: str, url: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            book = Book(title=title, price=price, url=url)
            session.add(book)


async def check_connection():
    await init_db()
    await add_book("Test_book", "f10.00", "http://books.toscrape.com/test")
    print("Book added successfully")


if __name__ == "__main__":
    asyncio.run(check_connection())
