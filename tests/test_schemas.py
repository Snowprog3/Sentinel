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
