from openai import OpenAI
import os


## Write teh code to read the openAI API key from a openai_key.env file
openai_key_path = "src/openai_key.env"
if os.path.exists(openai_key_path):
    # Read the API key from the file
    with open(openai_key_path, "r") as file:
        openai_key = file.read().strip()
else:
    print("Error: openai_key.env file not found.")
    exit(1)
# Set up the OpenAI client
print(openai_key)
client = OpenAI(api_key=openai_key)

def generate_response(prompt):
    try:
        # Make a request to the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the generated text from the response
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage
if __name__ == "__main__":
    user_prompt = "What is the capital of Maharashtra?"
    result = generate_response(user_prompt)
    print(f"User: {user_prompt}")
    print(f"AI: {result}")