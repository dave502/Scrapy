from pymongo import MongoClient
db_client = MongoClient('localhost', 27017)
db_friendships = db_client.instadata.friendships
# подписки
followers = db_friendships.find({"followed_to": "38299443164"})
print(followers)
db_users = db_client.instadata.users
users = db_users.find({'_id': {'$in': [user['follower'] for user in followers]}})
print('Подписчики:')
for user in users:
    print(user['username'])
# # подписки

