## When to use conversational agents? 
## When to use Assistant agents?
## When to use the Autogen library?


from autogen import ConversableAgent
from utility import  read_openai_key

# Set up OpenAI configuration   (this should be in a separate file)
llm_config =  {
            "model": "gpt-3.5-turbo",
            "api_key" : read_openai_key()
        }

# Create a Conversational agent (this is used for chatbots)
bret_agent = ConversableAgent(
    name="Bret",
    llm_config=llm_config,
    system_message = "You are Bret and you are standup comedian in two man comedy show"
)

jemaine_agent = ConversableAgent(
    name="Jemaine",
    llm_config=llm_config,
    system_message = "You are Jemain and you are standup comedian in two man comedy show"
)

# Initiate a chat between Bret and Jemaine
# Bret starts the conversation by asking Jemaine for a joke
# The conversation is limited to a maximum of 2 turns (1 exchange back and forth)
chat_result = bret_agent.initiate_chat(jemaine_agent, message="Hey Jemain, can you please tell me a good joke?", max_turns=2)

# Import the pprint module for prettier output formatting
import pprint

# Print the chat history (the conversation between Bret and Jemaine)
# This will show all messages exchanged during the conversation
pprint.pprint(chat_result.chat_history)

# Print the cost associated with this conversation
# This could represent API usage costs or computational resources used
pprint.pprint(chat_result.cost)










