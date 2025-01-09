# app/repositories/mongo_repository.py
from pymongo import MongoClient
from .base_repository import IDBRepository

class MongoRepository(IDBRepository):
    def __init__(self, mongo_uri: str, mongo_db: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    def insert(self, table: str, data: dict):
        """Insert data into a MongoDB collection (table equivalent)."""
        collection = self.db[table]
        try:
            result = collection.insert_one(data)
            return result.inserted_id  # Return the inserted ID of the document
        except Exception as e:
            print(f"Error inserting data into {table}: {e}")
            return None

    def select(self, table: str, conditions: dict):
        """Select data from a MongoDB collection based on conditions."""
        collection = self.db[table]
        try:
            result = collection.find(conditions)
            return list(result)  # Return results as a list of documents
        except Exception as e:
            print(f"Error selecting data from {table}: {e}")
            return []

    def remove_all_data(self, table: str):
        """Remove all data from a MongoDB collection."""
        collection = self.db[table]
        try:
            result = collection.delete_many({})
            return result.deleted_count  # Return number of documents deleted
        except Exception as e:
            print(f"Error removing data from {table}: {e}")
            return 0
