from utility import read_openai_key
from autogen import ConversableAgent, AssistantAgent

llm_config =  {
            "model": "gpt-3.5-turbo",
            "api_key" : read_openai_key()
        }

assistant_agent = AssistantAgent(
    name="AI_Assistant",
    llm_config=llm_config
)

agent = ConversableAgent(
    name="ChatBot",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

first_reply_from_agent = agent.generate_reply(messages=[{
    "content": "What is the capital of France?", "role": "user"
}])

print(first_reply_from_agent)