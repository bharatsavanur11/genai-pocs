from mongodb_conn import MongoDBConnection
import os

def get_mongodb_revenue_config():
    """Return MongoDB configuration details."""
    return {
        "uri": "mongodb+srv://hellobharat1:hellobharat1@sandbox.daamc.mongodb.net/?retryWrites=true&w=majority&appName=Sandbox",
        "database_name": "client_data",
        "collection_name": "oca_data"
    }

def get_json_file_path():
    """Return the path to the JSON file."""
    return os.path.join(
        os.path.dirname(__file__),
        "data",
        "oca_data.json"
    )

def insert_data_to_mongodb(mongo_conn, config, json_file_path):
    """Insert JSON data into MongoDB."""
    mongo_conn.insert_json_data(
        config["database_name"],
        config["collection_name"],
        json_file_path
    )

def main():
    """Main function to orchestrate the data insertion process."""
    config = get_mongodb_revenue_config()
    json_file_path = get_json_file_path()

    mongo_conn = MongoDBConnection(config["uri"])
    
    try:
        insert_data_to_mongodb(mongo_conn, config, json_file_path)
        print("Data insertion completed successfully.")
    except Exception as e:
        print(f"An error occurred during data insertion: {e}")
    finally:
        mongo_conn.close_connection()

if __name__ == "__main__":
    main()