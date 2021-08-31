# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class InstascraperPipeline:

    def __init__(self):
        # инициализация БД
        db_client = MongoClient('localhost', 27017)
        self.mongo_base = db_client.instadata

    def process_item(self, item, spider):
        # запись в БД
        collection_users = self.mongo_base['users']
        collection_users.update_one({'_id': item['_id']}, {'$set': item['user_info']}, upsert=True)

        collection_friendships = self.mongo_base['friendships']
        friendship = dict()
        friendship_id = ''
        if item['followed_by']:
            # подписчик
            friendship['follower'] = item['followed_by']
            # на кого подписан
            friendship['followed_to'] = item['_id']
            friendship_id = f'{item["followed_by"]}_{item["_id"]}'
        if item['followed_to']:
            # подписчик
            friendship['follower'] = item['_id']
            # на кого подписан
            friendship['followed_to'] = item['followed_to']
            friendship_id = f'{item["_id"]}_{item["followed_to"]}'
        collection_friendships.update_one({'_id': friendship_id}, {'$set': friendship}, upsert=True)

        return item
#  item
# {'_id': 3138951977,
#  'followed_by': None,
#  'followed_to': '38299443164',
#  'user_info': {'account_badges': [],
#                'follow_friction_type': 0,
#                'full_name': '',
#                'has_anonymous_profile_picture': False,
#                'is_private': True,
#                'is_verified': False,
#                'latest_reel_media': 0,
#                'pictures': [],
#                'pk': 3138951977,
#                'profile_pic_id': '2354791390562747222_3138951977',
#                'profile_pic_url': 'https://scontent-arn2-2.cdninstagram.com/v/t51.2885-19/s150x150/108519200_628701451185403_3576299443514381364_n.jpg?_nc_ht=scontent-arn2-2.cdninstagram.com&_nc_ohc=C6_YoW9L3moAX91SEZ6&edm=APQMUHMBAAAA&ccb=7-4&oh=d59d0b4d69dfc440cee710f352b59562&oe=6134A28F&_nc_sid=e5d0a6',
#                'username': 'sunny_wreath'}}