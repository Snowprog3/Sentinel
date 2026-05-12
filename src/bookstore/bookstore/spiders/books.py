import scrapy

class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com"]

    def parse(self, response):
        # Извлекаем все книги на текущей странице
        for book in response.css("article.product_pod"):
            yield {
                "title": book.css("h3 a::attr(title)").get(),
                "price": book.css("p.price_color::text").get(),
                "url": response.urljoin(book.css("h3 a::attr(href)").get()),
            }

        # Находим ссылку на следующую страницу и переходим по ней
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)