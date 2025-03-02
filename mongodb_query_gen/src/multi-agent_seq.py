## When to use conversational agents? 
## When to use Assistant agents?
## When to use the Autogen library?


from autogen import ConversableAgent
from utility import  read_openai_key

# Set up OpenAI configuration   (this should be in a separate file)
llm_config =  {
            "model": "gpt-4o",
            "api_key" : read_openai_key()
        }


## Defining agents used in the system

onboarding_personal_agent = ConversableAgent(
    name="Onboarding_Personal_Agent",
    system_message='''You are a helpful customer onboarding agent,
    you work for a phone provider called ACME.
    Your job is to gather the customer's name and location.
    Do not ask for any other information, only ask about the customer's name and location.
    After the customer gives you their name and location, repeat them 
    and thank the user, and ask the user to answer with TERMINATE to move on to describing their issue.
    ''',
    llm_config=llm_config,
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "terminate" in msg.get("content").lower(),
)


onboarding_issue_agent = ConversableAgent(
    name="Onboarding_Issue_Agent",
    system_message='''You are a helpful customer onboarding agent,
    you work for a phone provider called ACME,
    you are here to help new customers get started with our product.
    Your job is to gather the product the customer use and the issue they currently 
    have with the product,
    Do not ask for other information.
    After the customer describes their issue, repeat it and add
    "Please answer with 'TERMINATE' if I have correctly understood your issue." ''',
    llm_config=llm_config,
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "terminate" in msg.get("content").lower()
)

cusomter_engagement_agent = ConversableAgent(
    name="Customer Engagement Agent",
    llm_config=llm_config,
    system_message='''You are a helpful customer service agent.
    Your job is to gather customer's preferences on news topics.
    You are here to provide fun and useful information to the customer based on the user's
    personal information and topic preferences.
    This could include fun facts, jokes, or interesting stories.
    Make sure to make it engaging and fun!
    Return 'TERMINATE' when you are done.''',
    human_input_mode="NEVER",
     is_termination_msg=lambda msg: "terminate" in msg.get("content").lower(),
)

customer_proxy_agent = ConversableAgent(
    name="customer_proxy_agent",
    llm_config=False,
    code_execution_config=False,
    human_input_mode="ALWAYS",
)

## Store the sequence of agent information passing sequence
chats = []

chats.append(
    {
        "sender": onboarding_personal_agent,
        "recipient": customer_proxy_agent,
        "message": 
            "Hello, I'm here to help you solve any issue you have with our products. "
            "Could you tell me your name?",
        "summary_method": "reflection_with_llm",
        "summary_args": {
        "summary_prompt" : "Return the customer information "
                             "into a JSON object only: "
                             "{'name': '', 'location': ''}",
        },
        "max_turns": 2,
        "clear_history" : True
    }
)

chats.append(
    {
        "sender": onboarding_issue_agent,
        "recipient": customer_proxy_agent,
        "message": 
                "Great! Could you tell me what issue you're "
                "currently having and with which product?",
        "summary_method": "reflection_with_llm",
        "clear_history" : False
    }
)
chats.append(
        {
        "sender": customer_proxy_agent,
        "recipient": cusomter_engagement_agent,
        "message": "While we're waiting for a human agent to take over and help you solve "
        "your issue, can you tell me more about how you use our products or some "
        "topics interesting for you?",
        "max_turns": 2,
        "summary_method": "reflection_with_llm",
    }
)

print(chats)

from autogen import initiate_chats

chat_results = initiate_chats(chats)

import pprint
for chat_result in chat_results:
    pprint.pprint(chat_result)

