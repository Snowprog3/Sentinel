import uuid
from datetime import datetime, timezone

from scrapy import Spider

from bookstore.items import BookItem
from src.tracing import generate_trace_id


class BookDetailSpider(Spider):
    name = "books_detail"
    start_urls = ["http://books.toscrape.com"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_id = (
            f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:4]}"  # noqa
        )

    def parse(self, response):
        """Collect card of books from main page"""
        book_links = response.css("h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, self.parse_book)

        # Pagination catalog

    # next_page = response.css("li.next a::attr(href)").get()
    # next_page = response.css("h3 a::attr(href)").get()
    # if next_page:
    #     yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        """Extract data from card of book and save raw HTML"""
        item = BookItem()
        item["title"] = response.css("h1::text").get()
        item["price"] = response.css("p.price_color::text").get()
        item["url"] = response.url
        availability_text = response.css("p.instock.availability::text").getall()
        item["availability"] = " ".join(availability_text).strip()
        # Сохраняем весь HTML
        item["raw_data"] = {"html": response.text}
        item["trace_id"] = generate_trace_id()
        item["job_id"] = self.job_id
        yield item
