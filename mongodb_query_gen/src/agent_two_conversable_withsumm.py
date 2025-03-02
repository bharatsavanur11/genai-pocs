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
    system_message="You are Bret and you are standup comedian in two man comedy show. When you want to end the conversation, say 'I gotto go'",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "I gotta go" in msg["content"],
)

jemaine_agent = ConversableAgent(
    name="Jemaine",
    llm_config=llm_config,
    system_message="You are Jemain and you are standup comedian in two man comedy show. When you want to end the conversation, say 'I gotto go'",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "I gotta go" in msg["content"],
)

# Import the pprint module for prettier output formatting
import pprint


chat_result = bret_agent.initiate_chat(
    recipient=jemaine_agent,
    message="Hi I am Bret,Lets keep the jokes rolling,Lets start some jokes on LLMs",
)

pprint.pprint(chat_result.summary)










