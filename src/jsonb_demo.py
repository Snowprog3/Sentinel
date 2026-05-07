import asyncio

from crud import find_books_by_raw_field, get_books, insert_book
from database import AsyncSessionLocal
from schemas import BookCreate


async def main():
    async with AsyncSessionLocal() as session:
        book = BookCreate(
            title="Pro Docker",
            price="$35.00",
            url="http://books.toscrape.com/docker-book",
            raw_data={
                "rating": 4.5,
                "pages": 300,
                "tags": ["devops", "containers"],
                "publisher": "Apress",
            },
        )
        inserted = await insert_book(session, book)
        print(f"Inserted book with id - {inserted.id}")

        all_book = await get_books(session, limit=5)
        for b in all_book:
            print(f"[{b.id}] {b.title} | raw_data = {b.raw_data}")

        found = await find_books_by_raw_field(session, "publisher", "Apress")
        print(f"Books by Apress: {len(found)}")


if __name__ == "__main__":
    asyncio.run(main())
