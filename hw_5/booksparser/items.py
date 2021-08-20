# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    author = scrapy.Field()
    main_price = scrapy.Field()
    sale_price = scrapy.Field()
    rating = scrapy.Field()
