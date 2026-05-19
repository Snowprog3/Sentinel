from scrapy import Spider

from bookstore.items import BookItem


class BookDetailSpider(Spider):
    name = "books_detail"
    start_urls = ["http://books.toscrape.com"]

    def parse(self, response):
        """Collect card of books from main page"""
        book_links = response.css("h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, self.parse_book)

        # Pagination catalog
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

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
        yield item
