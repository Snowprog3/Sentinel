# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class BookItem(Item):
    """Define items"""
    url = Field()
    price = Field()
    availability = Field()
    title = Field()