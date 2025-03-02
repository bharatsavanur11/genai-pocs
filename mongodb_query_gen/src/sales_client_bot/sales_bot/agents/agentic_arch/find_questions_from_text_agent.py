import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', '..', '..')))

from sales_client_bot.sales_bot.utility import read_openai_key

from openai import OpenAI
import re

client = OpenAI(api_key=read_openai_key())

def clean_data(text):
        """Remove code block markers and language identifiers from the query text."""
        text = re.sub(r'```(?:python)?', '', text)
        text = re.sub(r'python', '', text)
        return text.strip()

def get_most_relevant_collections(extracted_collection_name, collection_name_list):
    prompt = f"""
    Given the extracted collection name "{extracted_collection_name}" and the list of available collections {collection_name_list},
    determine the nearest matching collections from the list.

    Instructions:
    1. Analyze the similarity between the extracted collection name and each collection in the list.
    2. Consider semantic relevance, not just exact matches.
    3. Consider the keyword search as well to find relevant collections.
    3. Return a list of the most relevant collections, sorted by relevance.
    4. If no collections are relevant, return an empty list.
    5. Limit the result to a maximum of 1 collections.

    Format the output as a Python list of strings.
    Example output: ["collection1", "collection2", "collection3"]
    """
    print("relevent colletion prompt:::", prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": ''' You are an AI assistant that
                  determines the most relevant collections based on given information.'''},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the generated text from the response
        result = response.choices[0].message.content.strip()
        print("results from openai comparison:", result)
        result = clean_data(result)
        # Convert the string representation of the list to an actual Python list
        relevant_collections = eval(result)

        return relevant_collections
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []

def generate_questions_array(text):
    prompt = f"""
    Analyze the following text and identify questions within it. 
    Return these questions as a Python string array.

    Text: "{text}"

    Instructions:
    1. Identify question from the given text.
    2. Format the output as a Python string array.
    3. Ensure each question ends with a question mark.

    Example output format: ["Question 1?"]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content":  ''' You are an AI assistant that identifies and 
                        formulates questions from given text. '''},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the generated text from the response
        result = response.choices[0].message.content.strip()
        
        # Convert the string representation of the array to an actual Python array
        questions_array = eval(result)
        return questions_array
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage   
if __name__ == "__main__":
    prompt = "Find all the clients see opportunies in cash equities business  and where revenue for client is greater than 1 billion"
    prompt1 = "Get all Relevant collections for question: " + prompt
    prompt2 = prompt1 + ". Return only the collection names in comma separated format"
    result = generate_questions_array(prompt2)

    # New code to generate questions array
    questions = generate_questions_array(prompt)
    print("Generated Questions:")
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")