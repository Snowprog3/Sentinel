from parsel import Selector


def extract_book_info(html: str) -> dict:
    """Extract title and price of the first page"""
    selector = Selector(text=html)
    title = selector.css("title::text").get(default="").strip()
    price = selector.css(".price_color::text").get(default="").strip()
    return {"title": title, "price": price}
