# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from functools import reduce


class LeroymerlinPipeline:
    def __init__(self):
        # инициализация БД
        db_client = MongoClient('localhost', 27017)
        self.mongo_base = db_client.Leroymerlin

    def process_item(self, item, spider):
        # id в виде lm_<идентификатор товара из url>
        item['_id'] = 'lm_' + item['url'].split('/')[-2]
        # после input_processor=MapCompose все свойства находятся в списке словарей, объединим их в один словарь
        props = reduce(lambda a, b: {**a, **b}, item['props'])
        item['props'] = props

        # запись в БД
        collection = self.mongo_base[spider.name]
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)

        return item

class LeroymerlinPhotoPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for photo in item['photos']:
                try:
                    yield scrapy.Request(photo)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [el[1] for el in results if el[1]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        # остаётся родное имя файла из ссылки
        img_name = request.url[request.url.rfind('/')+1:]
        # возращается путь в виде: <имя товара из ссылки в request>/full/<имя фото из ссылки на фото>
        return f'{item["url"].split("/")[-2]}/full/{img_name}'

