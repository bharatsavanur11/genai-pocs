import os
import autogen

def read_api_key(file_path):
    """Read the OpenAI API key from a file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError(f"Error: {file_path} file not found.")

def configure_assistant(api_key):
    """
    Configure and create an AI assistant using the provided API key.

    This function sets up the configuration for an AI assistant using the GPT-3.5-turbo model
    and creates an AssistantAgent with the specified configuration.

    Parameters:
    api_key (str): The OpenAI API key used for authentication.

    Returns:
    autogen.AssistantAgent: An instance of AssistantAgent configured with the provided API key
                            and model settings.
    """
    config_list = [
        {
            'model': 'gpt-3.5-turbo',
            'api_key': api_key,
        }
    ]
    return autogen.AssistantAgent(
        name="AI_Assistant",
        llm_config={
            "config_list": config_list,
        }
    )   
def configure_user_proxy():
    """Configure the user proxy."""
    return autogen.UserProxyAgent(
        name="Human",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "coding","use_docker":False},
    )

def run_conversation(user_proxy, assistant):
    """Run the conversation between user proxy and assistant."""
    user_proxy.initiate_chat(
        assistant,
        message="What is the capital of France? After answering, please end your message with TERMINATE"
    )
    user_proxy.send(
        "Now, can you write a simple Python function to calculate the factorial of a number? After providing the function, please end your message with TERMINATE"
    )

def main():
    try:
        # Read API key
        openai_key_path = "src/openai_key.env"
        api_key = read_api_key(openai_key_path)
        
        # Configure agents
        assistant = configure_assistant(api_key)
        user_proxy = configure_user_proxy()
        
        # Run conversation
        run_conversation(user_proxy, assistant)
    
    except FileNotFoundError as e:
        print(e)
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()