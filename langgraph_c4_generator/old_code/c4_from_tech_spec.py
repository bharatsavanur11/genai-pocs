from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List, Optional
import re
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY environment variable not set. Please set it to use OpenAI services.")
    api_key = "dummy-key"  # This will cause an error but allows the script to run for testing

# Define the state
class C4State(Dict[str, Any]):
    raw_spec: str
    components: Optional[List[Dict[str, str]]]
    relationships: Optional[List[Dict[str, str]]]
    missing_info: Optional[List[str]]
    summary: Optional[str]
    dsl: Optional[str]

# Agent 1: Parse components and relationships
def parse_spec_node(state: C4State) -> C4State:
    print("Parse Spec Node:", state)
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)
    raw_spec = state["raw_spec"]
    
    # LLM prompt to extract components and relationships
    prompt = f"""
    Given the following technical specification, identify the C4 components (name, type, description) and relationships (source, destination, description). Return the result as a JSON object with 'components' and 'relationships' keys. If the specification is unclear or lacks details, list the missing information under 'missing_info'.

    Specification:
    {raw_spec}

    Example output:
    {{
        "components": [
            {{"name": "Component1", "type": "Component", "description": "Does something"}},
            {{"name": "Component2", "type": "Component", "description": "Does something else"}}
        ],
        "relationships": [
            {{"source": "Component1", "destination": "Component2", "description": "Sends data to"}}
        ],
        "missing_info": ["Need more details about Component1's functionality"]
    }}
    """
    response = llm.invoke(prompt).content
    try:
        parsed = eval(response)  # Safely parse JSON-like string
        return {
            "components": parsed.get("components", []),
            "relationships": parsed.get("relationships", []),
            "missing_info": parsed.get("missing_info", [])
        }
    except:
        return {"missing_info": ["Failed to parse specification. Please clarify the description."]}

# Agent 2: Request missing information
def request_info_node(state: C4State) -> C4State:
    print("Request Info Node:", state)
    if not state.get("missing_info"):
        return {"missing_info": None}  # No missing info, proceed
    missing = state["missing_info"]
    prompt = f"""
    The following information is missing from the technical specification:
    {', '.join(missing)}
    
    Please provide a prompt to ask the user for clarification in a clear and concise manner.
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)
    response = llm.invoke(prompt).content
    return {"missing_info": response}

# Agent 3: Summarize requirements
def summarize_node(state: C4State) -> C4State:
    print("Summarize Node:", state)
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)
    prompt = f"""
    Summarize the following C4 components and relationships into a concise description of the system's requirements.

    Components:
    {state.get('components', [])}

    Example output:
    The system consists of a User Interface that sends requests to a Backend Service, which processes data and stores it in a Database. The Backend Service retrieves data from an External API.
    """
    summary = llm.invoke(prompt).content
    return {"summary": summary}

# Agent 4: Generate Structurizr DSL
def generate_dsl_node(state: C4State) -> C4State:
    print("Generate DSL Node:", state)
    components = state.get("components", [])
    relationships = state.get("relationships", [])
    
    dsl = ["workspace {\n", "    model {\n"]
    
    # Define system
    dsl.append('        system = softwareSystem "System" "The system described by the specification"\n')
    
    # Define components
    for comp in components:
        name = comp.get("name", "").replace(" ", "_").lower()
        desc = comp.get("description", "No description")
        dsl.append(f'        {name} = component "{comp.get("name", "Unknown")}" "{desc}"\n')
    
    # Define relationships
    for rel in relationships:
        source = rel.get("source", "").replace(" ", "_").lower()
        dest = rel.get("destination", "").replace(" ", "_").lower()
        desc = rel.get("description", "Interacts with")
        dsl.append(f'        {source} -> {dest} "{desc}"\n')
    
    dsl.append("    }\n")
    dsl.append("    views {\n")
    dsl.append('        component system "System_Component" "Component Diagram" {\n')
    dsl.append("            include *\n")
    dsl.append("        }\n")
    dsl.append("    }\n")
    dsl.append("}\n")
    
    return {"dsl": "".join(dsl)}

# Build the graph
graph = StateGraph(C4State)
graph.add_node("parse_spec", parse_spec_node)
graph.add_node("request_info", request_info_node)
graph.add_node("summarize", summarize_node)
graph.add_node("generate_dsl", generate_dsl_node)

# Define edges
graph.add_edge(START, "parse_spec")
graph.add_conditional_edges(
    "parse_spec",
    lambda state: "request_info" if state.get("missing_info") else "summarize",
    {
        "request_info": "request_info",
        "summarize": "summarize"
    }
)
graph.add_edge("request_info", END)  # Stop to wait for user input
graph.add_edge("summarize", "generate_dsl")
graph.add_edge("generate_dsl", END)

if __name__ == "__main__":
    # Example specification (based on previous LangGraph workflow)
    initial_spec = """
    The system is a LangGraph Workflow that processes user questions. It has three main components: 
    an Answer Node that uses an LLM to generate answers, a Validate Node that checks if the answer 
    contains the word "Python," and a Correction Node that rephrases the question if the answer is invalid. 
    The user initiates the workflow with a question. The Answer Node sends the answer to the Validate Node. 
    If the answer is valid, the workflow ends; otherwise, it goes to the Correction Node, which sends a 
    rephrased question back to the Answer Node.
    """
    initial_state = C4State({
        "raw_spec": initial_spec,
        "components": None,
        "relationships": None,
        "missing_info": None,
        "summary": None,
        "dsl": None
    })
    print("Initial State:", initial_state)
    app = graph.compile()
    for step in app.stream(initial_state):
        print(step)