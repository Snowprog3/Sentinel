# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

from scrapy import Item, Spider
from scrapy.exceptions import DropItem
from sqlalchemy.exc import IntegrityError

from src.crud import book_exists_by_url, insert_book
from src.database import AsyncSessionLocal
from src.schemas import BookCreate

logger = logging.getLogger(__name__)


class DatabasePipeline:
    async def _save_book(self, item: Item) -> bool:
        """Return True if a new row was inserted, False if URL already existed."""
        url = item.get("url")
        async with AsyncSessionLocal() as session:
            if await book_exists_by_url(session, url):
                logger.info(f"Skipping duplicate: {url}")
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
                logger.info(f"Saved to DB: {item.get('title')}")
        except IntegrityError:
            logger.warning(f"Duplicate skipped (IntegrityError): {item.get('url')}")
        except Exception as e:
            logger.error(f"Failed to save {item.get('title')}: {e}")
            raise DropItem(f"Database error = {e}")
        return item


class ValidationPipeline:
    def process_item(self, item, spider):
        # 1. Check title
        title = item.get("title")
        if not title:
            raise DropItem(f"Missing title: {item.get('url', 'no url')}")

        # 2. Check url
        url = item.get("url")
        if not url or "books.toscrape.com" not in url:
            raise DropItem(f"Invalid url: {url}")

        # 3. Check price
        price = item.get("price")
        if price and not (price.startswith("£") or price.startswith("$")):
            logger.warning(f"Unusual price format: {price} for {url}")

        logger.info(f"Valid item: {title}")
        return item
