
import sys
import os
from typing import List, Dict
import streamlit as st

sys.path.append(os.path .abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from agent_definitions import find_relevent_collection_agent, llm_config
from mongo_schema_defs import schemas, get_schema_keys
from autogen import ConversableAgent
from mongo_ops import MongoOps
from find_questions_from_text_agent import generate_questions_array, get_most_relevant_collections

def get_relevant_collections(question: str) -> List[str]:
    collection_names = find_relevent_collection_agent.generate_reply(messages=[{
        "role": "user", "content": question
    }])
    return [name.strip() for name in collection_names.split(',')]

def find_matching_collections(collection_list: List[str]) -> List[str]:
    new_collections = []
    for collection in collection_list:
        if collection in get_schema_keys():
            new_collections.append(collection)
            return new_collections[0]
        else:
            print(f"Finding most relevant schema for collection: {collection}...")
            result = get_most_relevant_collections(collection, get_schema_keys())
            print("New collection:", result)
            new_collections.append(result)
    return new_collections[0]

def generate_query_for_collection(collection: str, question: str) -> Dict[str, str]:
    prompt = f"""
    Generate a json MongoDB query for the '{collection}' collection based on this question: {question}. 
    Instructions:
    1. Analyze the Input: Understand the user's intent from the given natural language query.
    2. Identify Fields & Conditions: Extract relevant database fields, filters, and values.
    3. Generate a Valid MongoDB Query: Output a well-structured JSON query that follows MongoDB's syntax.
    4. Ensure Accuracy: The generated query should be syntactically correct and match the user's intent.
    5. Optimize Conditions: Use operators like $gt, $lt, $in,$regex, $and, $or when necessary.
    6. Also only return the generated mongo query without any additional text.
    7. Only Use the below mongodb collection schema:

    {schemas[collection]}

    Return only the mongo query
    """

    generate_mongodb_query_agent = ConversableAgent(
        name="relevant_collection_finder",
        llm_config=llm_config,
        system_message=prompt
    )

    mongo_query = generate_mongodb_query_agent.generate_reply(messages=[{
        "role": "user", "content": question
    }])

    return {"collection": collection, "query": mongo_query}

def run_conversations(multi_question: str) -> List[Dict[str, str]]:
    queries = []
    questions = generate_questions_array(multi_question)
    print('Questions:', questions)

    for i, question in enumerate(questions, 1):
        print(f"Question {i}: {question}")
        collection_list = get_relevant_collections(question)
        print(f"Relevant collections: {collection_list}")

        matching_collections = find_matching_collections(collection_list)

        for collection in matching_collections:
            query = generate_query_for_collection(collection, question)
            queries.append(query)

    return queries

def display_query_results(queries: List[Dict[str, str]]):
    st.subheader("Generated Queries:")
    for query in queries:
        st.write(f"Collection: {query['collection']}")
        st.code(query['query'], language='json')
        st.write("--------------------")

        results = MongoOps.clean_and_execute_mongo_query(query['query'], query['collection'])
        st.write("Query Results:")
        st.json(results)
        st.write("--------------------")

def main_ui():
    st.title("Client Data Extraction Tool")
    user_question = st.text_area("Enter your question:", height=100)

    if st.button("Generate Queries"):
        if user_question:
            queries = run_conversations(user_question)
            display_query_results(queries)
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main_ui()