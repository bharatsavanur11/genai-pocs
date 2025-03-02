import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', '..', '..')))

from sales_client_bot.sales_bot.utility import read_openai_key

from openai import OpenAI

client = OpenAI(api_key=read_openai_key())


def generate_questions_array(text):
    prompt = f"""
    Analyze the following text and identify two distinct questions within it. 
    Return these questions as a Python string array.

    Text: "{text}"

    Instructions:
    3. Format the output as a Python string array.
    4. Ensure each question ends with a question mark.

    Example output format: ["Question 1?", "Question 2?"]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that identifies and formulates questions from given text."},
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