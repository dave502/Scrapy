# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from itemloaders.processors import MapCompose, TakeFirst
import re


def get_item_properties(value):
    """возвращает пару ключ:значение из строки с характеристками товара"""
    try:
        # вариант передачи в Item характеристик по строкам и дальнейшее их разбиение на ключ-значение мне показался
        # более надёжным и предсказуемым (хоть и более затратным) чем парсинг всех элементов блока отдельно в один список
        return {value.split('<dt class="def-list__term">')[1].split('</dt>')[0].replace('\n', '').strip():
        value.split('<dd class="def-list__definition">')[1].split('</dd>')[0].replace('\n', '').strip()}
    except:
        return value


class LeroymerlinItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(lambda x: int(x.replace(' ', ''))),
                         output_processor=TakeFirst())
    photos = scrapy.Field()
    props = scrapy.Field(input_processor=MapCompose(get_item_properties))
    print()
