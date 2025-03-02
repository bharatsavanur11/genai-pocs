from numpy import size
from utility import read_openai_key
from openai import OpenAI
from pymongo import MongoClient
import sys
import os
import re
import json

# Add the parent directory of 'sales_bot' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def setup_openai_client():
    """Set up and return the OpenAI client."""
    openai_key = read_openai_key()
    return OpenAI(api_key=openai_key)

def generate_mongodbc_query(client, prompt):
    """Generate a MongoDB query using OpenAI's GPT model."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a MongoDB developer and you need to generate a MongoDB query."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

def clean_query_text(text):
    """Remove code block markers and language identifiers from the query text."""
    text = re.sub(r'```(?:json|javascript)?', '', text)
    text = re.sub(r'json|javascript', '', text)
    return text.strip()

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

def execute_mongodb_query(query):
    """Execute the MongoDB query and return results."""
    mongo_uri = "mongodb+srv://hellobharat1:hellobharat1@sandbox.daamc.mongodb.net/?retryWrites=true&w=majority&appName=Sandbox"
    database_name = "client_data"
    collection_name = "oca_data"

    try:
        with MongoClient(mongo_uri) as client:
            db = client[database_name]
            collection = db[collection_name]
            results = list(collection.find(query))
        return results
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    """Main function to orchestrate the query generation and execution process."""
    # Set up OpenAI configuration
    user_prompt = '''Can you please generate the MongoDB query for year 2023 
    having equities revenue greater than 2000000 using revenue_data collection with schema definition:
    {
      "_id": "str",
      "company": "str",
      "client_id": "str",
      "client_name": "str",
      "currency": "str",
      "year": "int",
      "region": "str",
      "last_updated": "str",
      "equities": "Int64",
      "derivatives": "Int64",
      "prime_brokerage": "int"
    }
    Generate just the JSON query that can be directly executed using MongoDB client and return query as text data.
    Enclose the property names and values in double quotes.'''

    openai_client = setup_openai_client()
    
    # Generate and process the query
    generated_query = generate_mongodb_query(openai_client, user_prompt)
    generated_query = '''
    {
         "Opportunity": { 
         "$regex": "robo-advisory"
         }
    }
    '''
    cleaned_query = clean_query_text(generated_query)
    parsed_query = parse_json_query(cleaned_query)
 
    
    if parsed_query:
        print("Parsed MongoDB Query:")
        print(json.dumps(parsed_query, indent=2))
        # Execute the query
        results  = execute_mongodb_query(parsed_query)
        print("\nQuery Results:")
        print(results)
        print(size(results))
        #print(json.dumps((results), indent=2))
    else:
        print("Failed to parse the generated query.")

if __name__ == "__main__":
    main()