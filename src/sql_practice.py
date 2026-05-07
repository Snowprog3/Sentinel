import asyncio

from crud import count_books, get_book_by_title, get_books, insert_book, update_price
from database import AsyncSessionLocal
from schemas import BookCreate


async def main():
    new_book = BookCreate(
        title="A Light in the Attic",
        price="f100.3",
        url="http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    )
    async with AsyncSessionLocal() as session:
        inserted = await insert_book(session, new_book)
        print(f"Inserted: {inserted.id} - {inserted.title}")

        books = await get_books(session, limit=5)
        print(f"\nFirst {len(books)} books")
        for b in books:
            print(f"{b.id} {b.title} - {b.price}")

        found = await get_book_by_title(session, "A Light in the Attic")
        print(f"\nFound {found.title if found else 'Not Found'}")

        if found:
            await update_price(session, found.id, "f59.2")
            print("Price updated")

        total = await count_books(session)
        print(f"\nTotal books - {total}")


if __name__ == "__main__":
    asyncio.run(main())
