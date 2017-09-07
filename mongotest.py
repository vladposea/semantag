#some file to play with mongo

import pymongo
client = pymongo.MongoClient("mongodb://vlad:asdasd@cluster0-shard-00-00-yo6cc.mongodb.net:27017,cluster0-shard-00-01-yo6cc.mongodb.net:27017,cluster0-shard-00-02-yo6cc.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")
db=client.test


articles = db.articles
#post_id = posts.insert_one(post).inserted_id
#print post_id
#for post in articles.find():
#	import pprint
#	pprint.pprint(post)

result=articles.update_many({},{"$rename": {" uri":"uri"}})
#result.updated_count