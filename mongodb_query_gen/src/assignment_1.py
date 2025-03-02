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

stephanie = ConversableAgent(
    name="Stephanie",
    llm_config=llm_config,
    system_message="Your name is Stephanie Kelton and you are a leading proponent of Modern Monetary Theory. "
    "Modern Monetary Theory (MMT) is a heterodox economic theory which states that governments should not worry about government borrowing but be willing to aim for full employment, achieving it through expansionary fiscal policy and financing by creating money. "
    "You are taking part in a debate about the future of money. "
    "When you're ready to end the conversation, say 'Thank you for having me'.",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "Thank you for having me" in msg["content"],
)

# Define agent Satoshi
satoshi = ConversableAgent(
    name="Satoshi",
    llm_config=llm_config,
    system_message="Your name is Satoshi Nakamoto and you are a the creator of Bitcoin. "
    "The monetary policy of Bitcoin, characterized by a fixed supply capped at 21 million coins, contrasts with the Modern Monetary Theory (MMT) approach. "
    "You are taking part in a debate about the future of money. "
    "When you're ready to end the conversation, say 'Thank you for having me.'.",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "Thank you for having me." in msg["content"],
)

# Initiate the chat
chat_result = stephanie.initiate_chat(
    recipient = satoshi, 
    message="I'm Stephanie Kelton, and I'm happy to be taking part in this debate about the future of money and monetary policy. "
    "I'd like to start by asking Satoshi why do they think that the government could not just provide a guaranteed job to all of its citizens?", 
)

import pprint
pprint.pprint(chat_result.summary)