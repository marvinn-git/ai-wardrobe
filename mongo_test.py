from pymongo import MongoClient

MONGO_URI = "mongodb+srv://lickythegreat_db_user:6sOFQIB6kZFpuhwd@cluster0.6nva1gz.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["ai_wardrobe"]
items = db["clothing_items"]

result = items.insert_one({"name": "test item", "category": "tshirt"})
print("Insertado con id:", result.inserted_id)

print("Primeros docs:")
for doc in items.find().limit(5):
    print(doc)
