import pytest
from pydantic import ValidationError

from src.schemas import NormalizedBook, ParsedBook, RawBookItem


class TestBookContracts:
    def test_raw_accepts_anything(self):
        raw = RawBookItem(title=None, price="bad", url=None)
        assert raw.title is None

    def test_parsed_rejects_invalid_url(self):
        with pytest.raises(ValidationError):
            ParsedBook(title="A", price="£10.00", url="not-a-url")

    def test_parsed_cleans_price(self):
        parsed = ParsedBook(title="A", price="£12,345.67", url="http://example.com")
        assert parsed.price == 12345.67

    def test_normalized_converts_url_to_string(self):
        parsed = ParsedBook(title="A", price="£10.00", url="http://example.com")
        norm = NormalizedBook(title=parsed.title, price=parsed.price, url=str(parsed.url))
        assert isinstance(norm.url, str)
        assert norm.url == "http://example.com/"


class TestFullContractPipeline:
    """Проверяет полный цикл Raw → Parsed → Normalized."""

    def test_full_valid_flow(self):
        raw = RawBookItem(title="A Book", price="£12.34", url="http://books.toscrape.com/test")
        parsed = ParsedBook(title=raw.title, price=raw.price, url=raw.url)
        norm = NormalizedBook(title=parsed.title, price=parsed.price, url=str(parsed.url))
        assert norm.price == 12.34
        assert norm.url == "http://books.toscrape.com/test"
        assert norm.title == "A Book"

    def test_missing_title_fails(self):
        with pytest.raises(ValidationError):
            ParsedBook(title=None, price="£10.00", url="http://books.toscrape.com/test")

    def test_invalid_url_fails(self):
        with pytest.raises(ValidationError):
            ParsedBook(title="A Book", price="£10.00", url="invalid-url")
