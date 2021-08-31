import scrapy
from scrapy.http import HtmlResponse
from pymongo import MongoClient
import re
import json
# from urllib.parse import urlencode
from copy import deepcopy
from hw_8.instascraper.items import InstascraperItem

class InstagramcomSpider(scrapy.Spider):
    name = 'instagramcom'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    users_parsed = ['baltrn_cafe', 'woo.dberry']
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    friendships_url = 'https://i.instagram.com/api/v1/friendships/'

    def __init__(self):
        super().__init__()
        # получаем авторизационные даные
        db_client = MongoClient('localhost', 27017)
        db_logins = db_client.private.log
        self.login_data = db_logins.find_one({"site": "instagram"})['auth']

    def parse(self, response: HtmlResponse):
        # отправляем login form
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata=self.login_data,
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        # если авторизовались - начинаем парсить пользоветелей из списка
        j_response = response.json()
        if j_response['authenticated']:
            for user in self.users_parsed:
                yield response.follow(f'/{user}',
                                      callback=self.user_start_parse,
                                      cb_kwargs={'username': user})

    def user_start_parse(self, response: HtmlResponse, username):
        # id анализируемого пользователя
        analized_user_id = self.fetch_user_id(response.text, username)

        # отправляем запрос на подписчиков
        followers_url = f'{self.friendships_url}{analized_user_id}/followers/?count=1000'
        yield response.follow(followers_url,
                              callback=self.get_user_friendships,
                              cb_kwargs={'analized_user_id': analized_user_id, 'searched_users_type': 'followers'})

        # отправляем запрос на подписки
        subscriptions_url = f'{self.friendships_url}{analized_user_id}/following/?count=1000'
        yield response.follow(subscriptions_url,
                              callback=self.get_user_friendships,
                              cb_kwargs={'analized_user_id': analized_user_id, 'searched_users_type': 'following'})

    def get_user_friendships(self, response: HtmlResponse, analized_user_id, searched_users_type):
        if response.status == 200:
            j_response = response.json()
            # будем получать по 1000 подписчиков|подписок за раз в цикле пока не получим всех
            if j_response.get('big_list'):
                users_url = f'{self.friendships_url}{analized_user_id}/{searched_users_type}/?count=1000&max_id={j_response.get("next_max_id")}'
                yield response.follow(users_url,
                                      callback=self.get_user_friendships,
                                      cb_kwargs={'analized_user_id': analized_user_id})

            # для каждого полученного подписчика|подписки отправляем запрос на его страничку
            users = j_response.get('users')
            for user in users:
                # user = {pk: < id >, username: < username >, full_name: < full_name >, is_private: false
                variables = {"id": str(user.get('pk')), "first": 12}
                user_url = f'{self.graphql_url}query_hash={self.posts_hash}&variables={json.dumps(variables)}'
                print(f'friendships user {user.get("username")} id {user.get("pk")} type {searched_users_type}')
                yield response.follow(user_url,
                                      callback=self.get_user_posts,
                                      cb_kwargs={'analized_user_id': analized_user_id,
                                                 'user_type':  searched_users_type,
                                                 'variables': deepcopy(variables),
                                                 'user_info': deepcopy(user)})

    def get_user_posts(self, response: HtmlResponse, analized_user_id, user_type, variables, user_info):
        if response.status == 200:
            j_response = response.json()
            posts = j_response.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')

            if not 'pictures' in user_info:
                user_info['pictures'] = []

            for post in posts:
                picture_link = post.get('node').get('display_url')
                picture_data = post.get('node')
                user_info['pictures'].append({'picture_link': picture_link,
                                              'picture_data': picture_data})

            page_info = j_response.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
                                                         # get('edge_web_feed_timeline').get('edges')
            if page_info.get('has_next_page'):
                 variables['after'] = page_info.get('end_cursor')
                 url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&variables={json.dumps(variables)}'
                 # url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
                 yield response.follow(url_posts,
                                      callback=self.get_user_posts,
                                      cb_kwargs={
                                          'analized_user_id': analized_user_id,
                                          'user_type': user_type,
                                          'variables': deepcopy(variables),
                                          'user_info': deepcopy(user_info)
                                      })
            else:  # если все посты пользователя отпарсили - возвращаем item
                item = InstascraperItem(_id=user_info['pk'],  # id пользователя
                                        # подписан на
                                        followed_to=analized_user_id if user_type == 'followers' else None,
                                        # кто подписан
                                        followed_by=analized_user_id if user_type == 'following' else None,
                                        user_info=deepcopy(user_info))  # вся информация о пользователе
                yield item


    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
