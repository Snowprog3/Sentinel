from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Book
from src.schemas import BookCreate


async def insert_book(session: AsyncSession, book: BookCreate) -> Book:
    """Insert new book and return ORM object"""
    db_book = Book(**book.model_dump())
    session.add(db_book)
    await session.flush()
    await session.commit()
    await session.refresh(db_book)
    return db_book


async def get_books(session: AsyncSession, limit: int = 10, offset: int = 0) -> list[Book]:
    """Return list of books with pagination"""
    stmt = select(Book).limit(limit).offset(offset)
    result = await session.execute(stmt)
    books = result.scalars().all()
    return list(books)


async def get_book_by_title(session: AsyncSession, title: str) -> Book | None:
    """Return book by title"""
    stmt = select(Book).where(Book.title == title)
    result = await session.execute(stmt)
    # Добавляем явное преобразование в list()
    book_seq = result.scalars().all()
    return list(book_seq)


async def update_price(session: AsyncSession, book_id: int, new_price: str) -> None:
    """Update book`s price by book_id"""
    stmt = update(Book).where(Book.id == book_id).values(price=new_price)
    await session.execute(stmt)
    await session.commit()


async def delete_book(session: AsyncSession, book_id: int) -> None:
    """Delete book by book_id"""
    stmt = delete(Book).where(Book.id == book_id)
    await session.execute(stmt)
    await session.commit()


async def count_books(session: AsyncSession) -> int | None:
    """Count the books"""
    stmt = select(func.count(Book.id))
    result = await session.execute(stmt)
    return result.scalar()


async def find_books_by_raw_field(session: AsyncSession, field: str, value: str) -> list[Book]:
    stmt = select(Book).where(Book.raw_data[field].as_string() == value)
    result = await session.execute(stmt)
    books = result.scalars().all()
    return list(books)
