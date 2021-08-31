# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstascraperItem(scrapy.Item):
    # id пользователя
    _id = scrapy.Field()
    # на кого подписан пользователь
    followed_to = scrapy.Field()
    # кто подписан на пользователя
    followed_by = scrapy.Field()
    # словарь со всей информацией о пользователе, включая список фотографий
    user_info = scrapy.Field()

