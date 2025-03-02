import re
import json
from pymongo import MongoClient
from mongodb_conn import MongoDBConnection

class MongoOps:
    @staticmethod
    def clean_query_text(text):
        """Remove code block markers and language identifiers from the query text."""
        text = re.sub(r'```(?:json|javascript)?', '', text)
        text = re.sub(r'json|javascript', '', text)
        return text.strip()

    @staticmethod
    def parse_json_query(text):
        """Parse the cleaned text into a JSON object."""
        try:
            # Ensure the text is enclosed in curly braces
            if not text.startswith('{'):

                text = '{' + text
            if not text.endswith('}'):
                text = text + '}'

            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None

    @staticmethod
    def clean_and_execute_mongo_query(query,collection_name):
        """
        Execute the MongoDB query and return results.

        Args:
            query (str): The MongoDB query as a string.

        Returns:
            list: A list of documents matching the query.
        """
        cleaned_query = MongoOps.clean_query_text(query)
        parsed_query = MongoOps.parse_json_query(cleaned_query)

        if parsed_query:
            print("Parsed MongoDB Query:")
            print(json.dumps(parsed_query, indent=2))
            print("Parsed Collection Name:",collection_name)

            # Execute the query
            results = MongoOps.execute_mongodb_query(parsed_query,collection_name)
            print("\nQuery Results:")
            #print(results)
            print(len(results))
            return results
        return None

    @staticmethod
    def execute_mongodb_query(parsed_query,collection_name):
        """
        Execute the MongoDB query.
        This method should be implemented to interact with your MongoDB database.
        """
        mongo_uri = "mongodb+srv://hellobharat1:hellobharat1@sandbox.daamc.mongodb.net/?retryWrites=true&w=majority&appName=Sandbox"
        database_name = "client_data"

        if collection_name == "Revenue":
            collection_name = "revenue_data"
        if collection_name == "Opportunity":
            collection_name = "oca_data"
        if collection_name =="Challenge":
            collection_name = "oca_data"

        print("Collection_name inside mongoops",collection_name)
        MongoDBConnection(mongo_uri)
        try:
            with MongoClient(mongo_uri) as client:
                db = client[database_name]
                collection = db[collection_name]
                results = list(collection.find(parsed_query,collection_name))
            return results
        except Exception as e:
            return f"An error occurred: {str(e)}"
            return []