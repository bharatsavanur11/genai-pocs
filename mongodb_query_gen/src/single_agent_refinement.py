## When to use Assistant agents?
## When to use the Autogen library?


from autogen import ConversableAgent,AssistantAgent
from utility import  read_openai_key

# Set up OpenAI configuration   (this should be in a separate file)
llm_config =  {
            "model": "gpt-4o",
            "api_key" : read_openai_key()
        }

task = '''
    Write a blog post related to revenue of the Google over the period of last 10 years and compare how it has 
    performed with other tech companies like Apple, Microsoft, Amazon, and Facebook.  Can you also include the new source
    to corralate the data?
'''
writer_assistant = AssistantAgent(
    llm_config=llm_config,
    name="Writer",
    system_message="You are a writer. You write engaging and concise " 
        "blogposts (with title) on given topics. You must polish your "
        "writing based on the feedback you receive and give a refined "
        "version. Only return your final work without additional comments.",
)


result = writer_assistant.generate_reply(messages=[{"content": task, "role": "user" }])

critic_assistant = AssistantAgent(
    llm_config=llm_config,
    name="Critic",
    system_message='''You are a critic. You evaluate the writing of others and provide constructive criticism. Please
    provide the relevance in financial context and how it can be applied to improve the blog post''')


chat_results =critic_assistant.initiate_chat(
                recipient=writer_assistant,
                message=task,
                max_turns=2,
                summary_method="last_msg")
                               


import pprint

pprint.pprint(chat_results.summary)