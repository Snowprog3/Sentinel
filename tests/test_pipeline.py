import pytest
from bookstore.items import BookItem
from bookstore.pipelines import ValidationPipeline
from scrapy.exceptions import DropItem


def test_valid_item():
    pipeline = ValidationPipeline()
    item = BookItem()
    item["title"] = "Test Book"
    item["price"] = "£10.00"
    item["url"] = "http://books.toscrape.com/test"
    item["raw_data"] = {"html": "<p>Test</p>"}

    processed = pipeline.process_item(item, None)
    assert processed["title"] == "Test Book"
    assert processed["price"] == "10.0"  # очищено
    assert processed["url"] == "http://books.toscrape.com/test"


def test_invalid_url():
    pipeline = ValidationPipeline()
    item = BookItem()
    item["title"] = "Bad"
    item["price"] = "£10.00"
    item["url"] = "not-a-url"
    with pytest.raises(DropItem):
        pipeline.process_item(item, None)
