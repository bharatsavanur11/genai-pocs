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

    ## write the code to return the collection when a name is provided
    def get_collection(self, database_name, collection_name):
        client = self.get_connection()
        if not client:
            return None
        db = client[database_name]
        return db[collection_name]




