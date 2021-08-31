from pymongo import MongoClient
db_client = MongoClient('localhost', 27017)
db_friendships = db_client.instadata.friendships
# подписчики
# тут можно было бы, конечно, сделать запросы покрасивее
# ищем список id подписчиков в коллекции friendships
followers = db_friendships.find({"followed_to": "38299443164"})
# ищем данные подписчиков в коллекции users
db_users = db_client.instadata.users
users = db_users.find({'_id': {'$in': [user['follower'] for user in followers]}})
print('Подписчики:')
for user in users:
    print(user['username'])
# подписки
subscriptions = db_friendships.find({"follower": "38299443164"})
# ищем данные подписок в коллекции users
db_users = db_client.instadata.users
users = db_users.find({'_id': {'$in': [user['followed_to'] for user in followers]}})
print('Подписки:')
for user in users:
    print(user['username'])


