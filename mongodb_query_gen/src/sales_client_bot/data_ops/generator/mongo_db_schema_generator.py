from pymongo import MongoClient
from bson import json_util
import json

def get_mongodb_revenue_config():
    """Return MongoDB configuration details."""
    return {
        "uri": "mongodb+srv://hellobharat1:hellobharat1@sandbox.daamc.mongodb.net/?retryWrites=true&w=majority&appName=Sandbox",
        "database_name": "client_data",
        "collection_name": "revenue_data"
    }

def get_mongodb_oca_config():
    """Return MongoDB configuration details."""
    return {
        "uri": "mongodb+srv://hellobharat1:hellobharat1@sandbox.daamc.mongodb.net/?retryWrites=true&w=majority&appName=Sandbox",
        "database_name": "client_data",
        "collection_name": "oca_data"
    }


def connect_to_mongodb(uri):
    """Connect to MongoDB and return the client."""
    return MongoClient(uri)

def get_collection_schema(collection):
    """Fetch and return the schema of the collection."""
    # Get a sample document
    sample_doc = collection.find_one()
    
    if not sample_doc:
        return None
    
    # Function to recursively build schema
    def build_schema(obj):
        if isinstance(obj, dict):
            return {k: build_schema(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [build_schema(obj[0])] if obj else []
        else:
            return type(obj).__name__
    
    return build_schema(sample_doc)

def main(config, output_file_name):
    client = connect_to_mongodb(config['uri'])
    
    try:
        db = client[config['database_name']]
        collection = db[config['collection_name']]
        
        schema = get_collection_schema(collection)
        
        if schema:
            # Convert schema to JSON and print
            schema_json = json.dumps(schema, indent=2, default=json_util.default)
            print(f"Schema for collection '{config['collection_name']}':")
            print(schema_json)
            
            # Save the schema to a file
            output_file = f"/Users/bharatsavanur/Desktop/projects/agents/assignment_1/src/sales_client_bot/data_ops/data/{output_file_name}"
            with open(output_file, 'w') as f:
                f.write(schema_json)
            print(f"Schema has been saved to {output_file}")
        else:
            print(f"No documents found in the collection '{config['collection_name']}'")
    
    finally:
        client.close()

if __name__ == "__main__":
    # Example usage for revenue data
    revenue_config = get_mongodb_revenue_config()
    main(revenue_config, "revenue_data_schema.json")

    # Example usage for OCA data
    oca_config = get_mongodb_oca_config()
    main(oca_config, "oca_data_schema.json")