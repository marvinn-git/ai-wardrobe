import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("Falta MONGO_URI en el archivo .env")

client = MongoClient(MONGO_URI)
db = client["ai_wardrobe"]

users = db["users"]
clothing_items = db["clothing_items"]
profiles = db["profiles"]
outfits = db["outfits"]