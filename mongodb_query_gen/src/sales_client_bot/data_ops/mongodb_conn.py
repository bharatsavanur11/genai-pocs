from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json

class MongoDBConnection:
    def __init__(self, uri):
        self.uri = uri
        self.client = None

    def get_connection(self):
        if not self.client:
            try:
                self.client = MongoClient(self.uri, server_api=ServerApi('1'))
                # Send a ping to confirm a successful connection
                self.client.admin.command('ping')
                print("Pinged your deployment. You successfully connected to MongoDB!")
            except Exception as e:
                print(f"An error occurred while connecting to MongoDB: {e}")
                return None
        return self.client

    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None
            print("MongoDB connection closed.")

    def insert_json_data(self, database_name, collection_name, json_file_path):
        client = self.get_connection()
        if not client:
            return

        try:
            db = client[database_name]
            collection = db[collection_name]

            with open(json_file_path, 'r') as file:
                json_data = json.load(file)

            if isinstance(json_data, list):
                result = collection.insert_many(json_data)
                print(f"Inserted {len(result.inserted_ids)} documents into the collection.")
            elif isinstance(json_data, dict):
                result = collection.insert_one(json_data)
                print(f"Inserted 1 document into the collection with id: {result.inserted_id}")
            else:
                print("Invalid JSON data format. Expected a list of documents or a single document.")

        except Exception as e:
            print(f"An error occurred while inserting data: {e}")
        finally:
            self.close_connection()