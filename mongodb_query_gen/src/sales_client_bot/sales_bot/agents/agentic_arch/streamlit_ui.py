import streamlit as st
from agent_definitions import find_relevent_collection_agent, llm_config
from mongo_schema_defs import schemas, get_schema_keys
from autogen import ConversableAgent
from mongo_ops import MongoOps
from find_questions_from_text_agent import generate_questions_array, get_most_relevant_collections

def generate_query_for_collection(collection: str, question: str):
    prompt = f'''Generate a MongoDB query for the '{collection}' collection based on this question: {question}. 
                    Instructions:
                    Analyze the Input: Understand the user's intent from the given natural language query.
        Identify Fields & Conditions: Extract relevant database fields, filters, and values.
        Generate a Valid MongoDB Query: Output a well-structured JSON query that follows MongoDB's syntax.
        Ensure Accuracy: The generated query should be syntactically correct and match the user's intent.
        Optimize Conditions: Use operators like $gt, $lt, $in, $regex, $and, $or when necessary.
        Also only return the generated mongo query without any additional text.
        Only Use the below mongodb collection schema:

    '''
    prompt = prompt + str(schemas[collection])
    prompt = prompt + ''' . Return only the mongo query'''

    generate_mongodb_query_agent = ConversableAgent(
        name="relevant_collection_finder",
        llm_config=llm_config,
        system_message=prompt
    ) 

    mongo_query = generate_mongodb_query_agent.generate_reply(messages=[{
        "role": "user", "content": question
    }])

    return mongo_query

def run_conversations(question):
    queries = []
    questions = generate_questions_array(question)
    
    for i, sub_question in enumerate(questions, 1):
        collection_names = find_relevent_collection_agent.generate_reply(messages=[{
            "role": "user", "content": sub_question
        }])

        collection_list = [name.strip() for name in collection_names.split(',')]
        
        new_collections = []
        for collection in collection_list:
            if collection in get_schema_keys():
                new_collections.append(collection)
            else:
                result = get_most_relevant_collections(collection, get_schema_keys())
                new_collections.extend(result)

        for collection in new_collections:
            mongo_query = generate_query_for_collection(collection, sub_question)
            queries.append({"collection": collection, "query": mongo_query})

    return queries

def main():
    st.title("MongoDB Query Generator")

    user_question = st.text_area("Enter your question:", height=100)

    if st.button("Generate Queries"):
        if user_question:
            queries = run_conversations(user_question)

            st.subheader("Generated Queries:")
            for query in queries:
                st.write(f"Collection: {query['collection']}")
                st.code(query['query'], language='json')
                st.write("--------------------")

                # Execute the query and display results
                results = MongoOps.clean_and_execute_mongo_query(query['query'], query['collection'])
                st.write("Query Results:")
                st.json(results)
                st.write("--------------------")
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()