import os

 def read_openai_key():
    key = read_api_key("src/openai_key.env")
    print(key)
    return key

def read_api_key(file_path):
    """Read the OpenAI API key from a file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError(f"Error: {file_path} file not found.")