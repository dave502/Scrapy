# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class BooksparserPipeline:
    def __init__(self):
        db_client = MongoClient('localhost', 27017)
        self.mongo_base = db_client.books

    def process_item(self, item, spider):
        item['_id'] = spider.name + '_' + item['url'].replace('https://book24.ru/product/', '')[:-1]
        item['name'] = item['name'].replace("\n", "").strip()

        if not item['main_price']:  # есть нет старой цены (product-sidebar-price__price-old) - значит скидки нет,
            # и основная цена находится на месте скидочной
            item['main_price'] = item['sale_price']
            item['sale_price'] = None

        item['main_price'] = int(''.join(filter(str.isdecimal, item['main_price']))) if item['main_price'] else None # None - если книги нет в наличии
        item['sale_price'] = int(item['sale_price']) if item['sale_price'] else None
        item['rating'] = float(item['rating'].replace("\n", "").replace(",", ".").strip())

        collection = self.mongo_base[spider.name]
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)

        return item
