from scrapy import Spider

from bookstore.items import BookItem


class BooksSpider(Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com"]

    def parse(self, response):
        # Извлекаем все книги на текущей странице
        for book in response.css("article.product_pod"):
            item = BookItem()
            item["title"] = book.css("h3 a::attr(title)").get()
            item["price"] = book.css("p.price_color::text").get()
            item["url"] = response.urljoin(book.css("h3 a::attr(href)").get())
            availability_text = book.css("p.instock.availability::text").getall()
            item["availability"] = " ".join(availability_text).strip()
            yield item

        # Находим ссылку на следующую страницу и переходим по ней
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
