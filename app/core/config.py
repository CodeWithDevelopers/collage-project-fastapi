# app/core/config.py

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"  # Or your actual connection string
DATABASE_NAME = "HUM_AI_DB"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client[DATABASE_NAME]

def get_database():
    return database
