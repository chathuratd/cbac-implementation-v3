from pymongo import MongoClient

# Direct MongoDB connection with auth
client = MongoClient("mongodb://admin:admin123@localhost:27017/")
db = client["cbac_system"]

behaviors_count = db.behaviors.count_documents({})
print(f"Total behaviors: {behaviors_count}")

# Find actual user_ids in the database
user_ids = db.behaviors.distinct('user_id')
print(f"Found user_ids: {user_ids}")

client.close()
