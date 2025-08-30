import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts.prompt import PromptTemplate
import os
import json
import re

# Set your OpenAI API key
###api_key = "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"
model = "gpt-4o-mini"

# Set up session state
if "chat_active" not in st.session_state:
    st.session_state.chat_active = True
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

st.title("🧠 Context-Aware Chat with LangChain")

# Exit button
if st.button("🚪 Exit Chat"):
    st.session_state.chat_active = False
    st.success("You have exited the chat.")
    st.stop()

# Continue only if chat is active
if st.session_state.chat_active:
    # LLM setup
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-4", api_key=api_key)

    memory = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=1000,
        return_messages=True
    )

    prompt_template = PromptTemplate(
        input_variables=["history", "input"],
        template="""
You are an expert Software Architect specializing in the C4 model approach and Structurizr DSL. Your role is to help me create accurate, comprehensive C4 diagrams for software systems using Structurizr DSL.

Process

I'll describe a system or application I want to model
You'll analyze my requirements and ask clarifying questions about:
    System context and boundaries
    Users, actors, and external systems
    Containers (applications, data stores, microservices)
    Components within important containers
    Key relationships and dependencies
    Technology choices and constraints
    Non-functional requirements that impact architecture
   and anything else not listed here but you think will be relevant to create a high quality diagram as output

Ask 1 question at a time.

DO NOT make any assumptions. If it is unclear, then ask questions.

Once you have sufficient information, you will:
Generate Structurizr DSL for the Context, Container, and Component levels
The DSL should be compatible for v1.32.0
Follow proper syntax and best practices
Include appropriate styles, icons, and relationships
Add relevant tags and metadata
Structure the DSL in a maintainable way
You will validate your DSL for:
Syntax errors
Logical inconsistencies
Missing elements
Proper relationship definition
Compliance with C4 model principles


{history}

Now answer the following question:

User: {input}
AI:"""
    )

    # New prompt for generating C4 diagram from conversation history
    c4_generation_prompt = PromptTemplate(
        input_variables=["conversation_history", "memory_summary"],
        template="""
You are an expert C4 model architect. Based on the complete conversation history and memory summary provided, generate a comprehensive Structurizr DSL for the system that was discussed.

CONVERSATION HISTORY:
{conversation_history}

MEMORY SUMMARY:
{memory_summary}

Instructions:
1. Analyze ALL the information provided in the conversation history and memory
2. Extract all mentioned components, relationships, actors, and system boundaries
3. Consider the historical context and evolution patterns discussed
4. Generate a complete Structurizr DSL that includes:
   - Context level (actors, software systems, external systems)
   - Container level (applications, data stores, microservices)
   - Component level (for key containers)
   - Proper relationships with descriptions
   - Appropriate tags and metadata
   - Styles and icons where relevant

5. Follow Structurizr DSL v1.32.0 syntax
6. Include comprehensive documentation in comments
7. Structure the DSL in a maintainable and readable way
8. Add any missing elements that would be logical based on the conversation context

Return ONLY the Structurizr DSL code, properly formatted and complete. Do not include any explanations or additional text outside the DSL code.
"""
    )

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt_template,
        verbose=True
    )

    # Sidebar for additional features
    st.sidebar.title("🛠️ Tools")
    
    # Generate C4 Diagram from Memory button
    if st.sidebar.button("🏗️ Generate C4 Diagram from Memory"):
        if memory.buffer:
            st.sidebar.info("Generating C4 diagram from conversation memory...")
            
            # Get conversation history
            conversation_text = ""
            for turn in st.session_state.conversation_history:
                user = turn.get("user", "")
                assistant = turn.get("assistant", "")
                if user:
                    conversation_text += f"User: {user}\n"
                if assistant:
                    conversation_text += f"Assistant: {assistant}\n"
            # Generate DSL using the conversation history
            c4_llm = ChatOpenAI(temperature=0.1, model_name="gpt-4", api_key=api_key)
            print(conversation_text)
            try:
                c4_response = c4_llm.invoke(
                    c4_generation_prompt.format(
                        conversation_history=conversation_text,
                        memory_summary=str(memory.buffer)
                    )
                )
                
                # Extract DSL from response
                dsl_content = c4_response.content
                
                # Clean up the response to extract just the DSL
                dsl_match = re.search(r'workspace\s*\{.*?\}', dsl_content, re.DOTALL)
                if dsl_match:
                    dsl_content = dsl_match.group()
                
                # Save to file
                filename = "c4_from_conversation.dsl"
                with open(filename, "w") as f:
                    f.write(dsl_content)
                
                st.sidebar.success(f"✅ DSL saved to {filename}")
                
                # Display the generated DSL
                with st.expander("📋 Generated C4 DSL", expanded=True):
                    st.code(dsl_content, language="dsl")
                    
            except Exception as e:
                st.sidebar.error(f"Error generating DSL: {str(e)}")
        else:
            st.sidebar.warning("No conversation memory available. Start chatting first!")

    # Clear memory button
    if st.sidebar.button("🗑️ Clear Memory"):
        memory.clear()
        st.session_state.conversation_history = []
        st.sidebar.success("Memory cleared!")

    user_input = st.text_input("Ask me anything:")

    if user_input:
        response = conversation.run(user_input)
        st.markdown(f"**Assistant:** {response}")
        
        # Store conversation in session state
        st.session_state.conversation_history.append({
            "user": user_input,
            "assistant": response
        })

        with st.expander("🔍 View Summary Context"):
            st.write(memory.buffer)
        
        with st.expander("📚 Full Conversation History"):
            for i, conv in enumerate(st.session_state.conversation_history, 1):
                st.markdown(f"**Turn {i}:**")
                st.markdown(f"**Assistant:** {conv['assistant']}")
                st.markdown("---")

    # Display current memory status
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Memory Status:**")
    st.sidebar.markdown(f"Conversation turns: {len(st.session_state.conversation_history)}")
    if memory.buffer:
        st.sidebar.markdown(f"Memory buffer: {len(memory.buffer)} messages")
    else:
        st.sidebar.markdown("Memory buffer: Empty")
