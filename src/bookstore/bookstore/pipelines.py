# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)


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
