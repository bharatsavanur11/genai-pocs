import os
import json
from typing import TypedDict, Annotated, Sequence
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.pydantic_v1 import BaseModel, Field

# Define the state of our graph.
# It will store the original specification and the identified components at each step.
class AgentState(TypedDict):
    """Represents the state of our agent's graph."""
    specification: str
    systems: str
    containers: str
    components: str
    relationships: str
    dsl_output: str

# Define Pydantic models for structured output from the LLM.
# This helps the LLM generate clean, structured JSON that we can parse.
class IdentifiedSystems(BaseModel):
    main_system_name: str = Field(description="The name of the main software system.")
    external_systems: Sequence[str] = Field(description="List of all external software systems.")

class IdentifiedContainers(BaseModel):
    containers: Sequence[str] = Field(description="List of containers within the main system.")
    container_tech: Sequence[str] = Field(description="Technology used for each container.")

class IdentifiedComponents(BaseModel):
    container_name: str = Field(description="The name of the container.")
    components: Sequence[str] = Field(description="List of components within this container.")
    component_tech: Sequence[str] = Field(description="Technology used for each component.")

class IdentifiedRelationships(BaseModel):
    relationships: Sequence[dict] = Field(description="A list of relationships between systems, containers, and components.")

# Helper function to generate and parse structured output from the LLM.
def generate_and_parse(llm, prompt, model_class):
    """Generates content from an LLM and parses it into a Pydantic model."""
    structured_llm = llm.with_structured_output(model_class)
    response = structured_llm.invoke(prompt)
    return response.json(indent=2)

# --- Define the LangGraph Nodes ---

def identify_systems(state):
    """Node 1: Identifies the main system and external systems."""
    print("--- Identifying Systems ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")
    prompt = f"""
    Given the following technical specification, identify the main software system and all external systems it interacts with.
    Specification: {state['specification']}
    Please provide the main system name and a list of external system names.
    """
    systems_data = generate_and_parse(llm, prompt, IdentifiedSystems)
    return {"systems": systems_data}

def infer_containers(state):
    """Node 2: Infers containers within the main system."""
    print("--- Inferring Containers ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")
    prompt = f"""
    Based on the following specification and identified systems, infer the main containers within the '{json.loads(state['systems'])['main_system_name']}' software system. For each container, suggest a technology stack.
    Specification: {state['specification']}
    Identified Systems: {state['systems']}
    Please provide a list of container names and their corresponding technologies.
    """
    containers_data = generate_and_parse(llm, prompt, IdentifiedContainers)
    return {"containers": containers_data}

def infer_components(state):
    """Node 3: Infers components within each container."""
    print("--- Inferring Components ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")
    components_list = []
    
    # Iterate through each container to identify its components
    containers_data = json.loads(state['containers'])
    for container_name in containers_data['containers']:
        prompt = f"""
        Based on the specification and the container '{container_name}', infer the components within it. Suggest a technology stack for each.
        Specification: {state['specification']}
        Container: {container_name}
        Please provide a list of components and their corresponding technologies for this specific container.
        """
        components_data = generate_and_parse(llm, prompt, IdentifiedComponents)
        components_list.append(components_data)
    
    return {"components": json.dumps(components_list)}

def map_relationships(state):
    """Node 4: Establishes relationships between all elements."""
    print("--- Mapping Relationships ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")
    prompt = f"""
    Based on the following system details, identify and describe all relationships between people, systems, containers, and components.
    Systems: {state['systems']}
    Containers: {state['containers']}
    Components: {state['components']}
    Please provide a list of relationships, each as a dictionary with 'source', 'destination', and 'description'.
    """
    relationships_data = generate_and_parse(llm, prompt, IdentifiedRelationships)
    return {"relationships": relationships_data}

def generate_dsl(state):
    """Node 5: Generates the final Structurizr DSL from all identified elements."""
    print("--- Generating DSL ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")
    prompt = f"""
    You are an expert at writing Structurizr DSL. Given the following identified elements and relationships, generate the complete Structurizr DSL code.
    - Context: {state['systems']}
    - Containers: {state['containers']}
    - Components: {state['components']}
    - Relationships: {state['relationships']}

    Generate a complete, valid Structurizr DSL string that includes a workspace, people, a software system, containers, components, and views for system context, container, and component diagrams. Ensure boundaries are clearly set.
    """
    dsl = llm.invoke(prompt).content
    return {"dsl_output": dsl}

# --- Build the LangGraph Workflow ---

def create_graph():
    """Builds and compiles the LangGraph state machine."""
    workflow = StateGraph(AgentState)

    # Add nodes for each step of the process
    workflow.add_node("identify_systems", identify_systems)
    workflow.add_node("infer_containers", infer_containers)
    workflow.add_node("infer_components", infer_components)
    workflow.add_node("map_relationships", map_relationships)
    workflow.add_node("generate_dsl", generate_dsl)

    # Define the flow of the graph
    workflow.set_entry_point("identify_systems")
    workflow.add_edge("identify_systems", "infer_containers")
    workflow.add_edge("infer_containers", "infer_components")
    workflow.add_edge("infer_components", "map_relationships")
    workflow.add_edge("map_relationships", "generate_dsl")
    workflow.add_edge("generate_dsl", END)

    return workflow.compile()

# --- Main execution block ---

if __name__ == "__main__":
    spec = """
    The Online Photo Editor is a web application that allows users to upload, edit, and share photos.
    The system uses a React-based frontend and a Node.js backend.
    The backend exposes a REST API to handle user authentication, image uploads, and editing operations.
    The application stores all user data and photos in a PostgreSQL database.
    Users can log in using their Google account via the Google Identity Service.
    When a photo is uploaded, a background worker service resizes the image for different devices and stores the thumbnails in a separate blob storage.
    The API service interacts with both the database and the background worker.
    """
    
    # Create and run the graph
    app = create_graph()
    result = app.invoke({"specification": spec})
    
    # Print the final DSL output
    print("\n\n--- Generated Structurizr DSL ---")
    print(result['dsl_output'])
