import sys
import os



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..', '..')))

from sales_client_bot.sales_bot.utility import read_openai_key
from sales_client_bot.data_ops.load_data.load_client_data import load_json_data

from openai import OpenAI

find_relevent_collection_query_role =  ""
find_relevent_collection_query_instructions = """
Role: You are an expert in database architecture and MongoDB. Your task is to analyze a natural language search query and determine the most relevant MongoDB collections where the requested data is most likely stored.

Instructions:

Analyze the Input: Understand the user’s intent from the given natural language query.
Identify Fields & Conditions: Extract relevant database fields, filters, and values.
Generate a Valid MongoDB Query: Output a well-structured JSON query that follows MongoDB’s syntax.
Ensure Accuracy: The generated query should be syntactically correct and match the user’s intent.
Optimize Conditions: Use operators like $gt, $lt, $in, $regex, $and, $or when necessary.
Only Use the below mongodb collection schema:

Opportunity Schema:
 {
    "clientID": "GC001",
    "clientName": "Delta Trust Inc.",
    "Opportunity": "Launch digital wealth management platform"
  },
"""


client = OpenAI(api_key=read_openai_key())

def generate_response(prompt):
    try:
        # Make a request to the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role":"system" , "content": find_relevent_collection_query_instructions},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the generated text from the response
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage   
if __name__ == "__main__":
    prompt = "Find all the clients see opportunities in cash equities business  and where revenue for client is greater than 1 billion"
    prompt1 = "Generate the mongo query using the context provided in schema : " + prompt
    result = generate_response(prompt1)
   # print(f"User: {find_relevent_collection_query_role}")
    print(f"AI: {result}")