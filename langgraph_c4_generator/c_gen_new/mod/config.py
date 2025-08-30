import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def get_llm(model: str = "gpt-4.1", temperature: float = 0.1) -> ChatOpenAI:
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set. Please set it.")
    return ChatOpenAI(model=model, api_key=api_key, temperature=temperature)


