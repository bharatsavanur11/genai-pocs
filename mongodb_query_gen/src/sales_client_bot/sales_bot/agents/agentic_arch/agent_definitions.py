# Create a Conversational agent (this is used for chatbots)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..', '..')))


from autogen import ConversableAgent

from sales_client_bot.sales_bot.utility import read_openai_key
from sales_client_bot.data_ops.load_data.load_client_data import load_json_data

from openai import OpenAI
from autogen import ConversableAgent, AssistantAgent

llm_config =  {
            "model": "gpt-4o",
            "api_key" : read_openai_key()
        }

find_relevent_collection_agent = ConversableAgent(
    name="relevant_collection_finder",
    llm_config=llm_config,
    system_message='''
     Role: You are an expert in database architecture and MongoDB. 
     Your task is to analyze a natural language search query and determine the most relevant 
     MongoDB collections using below instructions.
     Return only the collection names in comma separated format.
     Instructions:
     Use only the below defined collections to find matching names:

    Opportunity Schema:
    {
        "clientID": "GC001",
        "clientName": "Delta Trust Inc.",
        "Opportunity": "Launch digital wealth management platform"
      },

    Challenge Schema:
    {
        "clientID": "GC001",
        "clientName": "Delta Trust Inc.",
        "Challenge": "Enhance digital wealth management platform security"
      },
      AcitionItem Schema: 
      {
        "clientID": "GC001",
        "clientName": "Delta Trust Inc.",
        "ActionItem": "Implement a comprehensive security strategy for digital wealth management platform"
      }
      Revenue Schema:
      {
        "_id": "6797aa61af157dc5a5f6321f",
        "company": "Sigma Invest Inc.",
        "client_id": "GC002",
        "client_name": "Sigma Invest Inc.",
        "currency": "USD",
        "year": 2015,
        "region": "Global",
        "last_updated": "2024-08-22T15:46:41.529041",
        "equities": 2930080389,
        "derivatives": 1971112342,
        "prime_brokerage": 1863227667
      }
        '''
    )

generate_mongodb_query_agent = ConversableAgent(
        name="query_generator_agent",
        llm_config=llm_config,
        system_message= ''' Role: You are an expert in database querying and MongoDB. 
        Your task is to convert user-provided natural language search queries into a valid and optimized 
        MongoDB query.
        Instructions:

    Analyze the Input: Understand the user’s intent from the given natural language query.
    Identify Fields & Conditions: Extract relevant database fields, filters, and values.
    Generate a Valid MongoDB Query: Output a well-structured JSON query that follows MongoDB’s syntax.
    Ensure Accuracy: The generated query should be syntactically correct and match the user’s intent.
    Optimize Conditions: Use operators like $gt, $lt, $in, $regex, $and, $or when necessary.
    Only Use the below mongodb collection:

   '''
)