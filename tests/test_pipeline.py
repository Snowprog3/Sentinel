from unittest.mock import MagicMock

import pytest
from bookstore.items import BookItem
from bookstore.pipelines import ValidationPipeline
from scrapy.exceptions import DropItem


@pytest.fixture
def spider():
    return MagicMock(name="books_detail")


def test_valid_item(spider):
    pipeline = ValidationPipeline()
    item = BookItem()
    item["title"] = "Test Book"
    item["price"] = "£10.00"
    item["url"] = "http://books.toscrape.com/test"
    item["raw_data"] = {"html": "<p>Test</p>"}

    processed = pipeline.process_item(item, spider)
    assert processed["title"] == "Test Book"
    assert processed["price"] == "10.0"  # очищено
    assert processed["url"] == "http://books.toscrape.com/test"


def test_invalid_url(spider):
    pipeline = ValidationPipeline()
    item = BookItem()
    item["title"] = "Bad"
    item["price"] = "£10.00"
    item["url"] = "not-a-url"
    with pytest.raises(DropItem):
        pipeline.process_item(item, spider)
