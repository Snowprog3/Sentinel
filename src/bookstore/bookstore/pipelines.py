# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

from pydantic import ValidationError
from scrapy import Item, Spider
from scrapy.exceptions import DropItem
from sqlalchemy.exc import IntegrityError

from src.crud import book_exists_by_url, insert_book
from src.database import AsyncSessionLocal
from src.schemas import BookCreate, NormalizedBook, ParsedBook, RawBookItem

logger = logging.getLogger(__name__)


class DatabasePipeline:
    async def _save_book(self, item: Item) -> bool:
        """Return True if a new row was inserted, False if URL already existed."""
        url = item.get("url")
        async with AsyncSessionLocal() as session:
            if await book_exists_by_url(session, url):
                logger.debug("Skipping duplicate: %s", url)
                return False
            book_data = BookCreate(
                title=item.get("title"),
                price=item.get("price"),
                url=url,
                raw_data=item.get("raw_data"),
            )
            await insert_book(session, book_data)
            return True

    async def process_item(self, item: Item, spider: Spider) -> Item:
        try:
            if await self._save_book(item):
                logger.debug("Saved to DB: %s", item.get("title"))
        except IntegrityError:
            logger.warning(f"Duplicate skipped (IntegrityError): {item.get('url')}")
        except Exception as e:
            logger.error(f"Failed to save {item.get('title')}: {e}")
            raise DropItem(f"Database error = {e}")
        return item


class ValidationPipeline:
    def process_item(self, item: Item, spider: Spider) -> Item:
        # 1. Save raw data
        raw = RawBookItem(**dict(item))

        try:
            # 2. Try clean and validation
            parsed = ParsedBook(
                title=raw.title,
                price=raw.price,
                url=raw.url,
            )
        except ValidationError as e:
            url = item.get("url")
            logger.warning("Dropped %s: %s", url, e.errors())
            raise DropItem(f"Validation failed for {url!r}: {e.errors()}") from e

        # 3 Normalized version for DB
        norm = NormalizedBook(
            title=parsed.title,
            price=parsed.price,
            url=str(parsed.url),
            raw_data=item.get("raw_data"),
        )
        # 4 Renew item
        item["title"] = norm.title
        item["price"] = str(norm.price) if norm.price else None
        item["url"] = norm.url
        logger.debug("Validate: %s", norm.title)
        return item
