import pytest
from sqlalchemy import select

from src.crud import insert_book
from src.database import AsyncSessionLocal
from src.models import Book
from src.schemas import BookCreate


@pytest.mark.asyncio
async def test_and_insert_book():
    "Check insert and reading book for a CRUD-function"
    book_data = BookCreate(
        title="Integration Book Test",
        price="$9.99",
        url="http://books.toscrape.com/integration-test",
        raw_data={"rating": 4.5, "pages": 200},
    )

    async with AsyncSessionLocal() as session:
        """Insert"""
        inserted = await insert_book(session, book_data)
        assert inserted.id is not None
        assert inserted.title == "Integration Book Test"

        """Reading"""
        stmt = select(Book).where(Book.id == inserted.id)
        result = await session.execute(stmt)
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.price == "$9.99"
        assert found.raw_data == {"rating": 4.5, "pages": 200}

        await session.delete(found)
        await session.commit()
