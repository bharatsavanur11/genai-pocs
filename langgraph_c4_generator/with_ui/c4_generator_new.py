#!/usr/bin/env python3
"""
C4 Architecture Generator using LangGraph

This module provides a comprehensive solution for generating C4 architecture diagrams
from technical specifications using LangGraph workflow. It can generate:

1. System Context Diagrams (Level 1)
2. Container Diagrams (Level 2) 


The system uses multiple specialized agents to:
- Parse and analyze technical specifications
- Identify systems, containers, and components
- Establish relationships and boundaries
- Generate Structurizr DSL code
"""

import json
import os
from pathlib import Path
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Union

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

# Load environment variables
load_dotenv()
example_dsl = """
workspace "My Web Application" "A sample web application." {

    model {
        // Actors
        user = person "Customer" "A customer of the web application."

        // External Systems
        emailSystem = softwareSystem "E-mail System" "The internal e-mail system."
        paymentGateway = softwareSystem "Payment Gateway" "External system for processing payments."

        // Internal System
        webapp = softwareSystem "My Web Application" "Allows customers to browse products and make purchases." {
            webApplication = container "Web Application" "Provides the user interface and handles business logic." "Java Spring Boot"
            database = container "Database" "Stores product information, customer data, and orders." "PostgreSQL Database"
            apiGateway = container "API Gateway" "Manages API requests and routes them to the appropriate services." "Nginx"
            orderService = container "Order Service" "Handles order creation and management." "Java Spring Boot Microservice"
            productService = container "Product Service" "Manages product catalog and inventory." "Java Spring Boot Microservice"

            // Relationships within the system
            user -> webApplication "Uses"
            webApplication -> apiGateway "Makes API calls to"
            apiGateway -> orderService "Routes order requests to"
            apiGateway -> productService "Routes product requests to"
            orderService -> database "Reads from and writes to"
            productService -> database "Reads from"
            orderService -> emailSystem "Sends order confirmation emails via"
            orderService -> paymentGateway "Initiates payments via"
        }
    }

    views {
        // System Context Diagram
        systemContext webapp "SystemContext" {
            include *
            autoLayout
        }

        // Container Diagram
        container webapp "Containers" {
            include *
            autoLayout
        }
    }
}
"""
import streamlit as st
from openai import OpenAI

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
        # Access the OpenAI API key from the secrets
    api_key = st.secrets["OPENAI_API_KEY"]
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set. Please set it to use OpenAI services.")

# Define the state structure
class C4State(TypedDict):
    raw_spec: str
    systems: Optional[List[Dict[str, Any]]]
    containers: Optional[List[Dict[str, Any]]]
    components: Optional[List[Dict[str, Any]]]
    relationships: Optional[List[Dict[str, Any]]]
    external_systems: Optional[List[Dict[str, Any]]]
    personas: Optional[List[Dict[str, Any]]]
    user_experience: Optional[Dict[str, Any]]
    missing_info: Optional[List[str]]
    summary: Optional[str]
    dsl_context: Optional[str]
    dsl_container: Optional[str]
    dsl_component: Optional[str]
    dsl_context_container: Optional[str]
    dsl_user_centric: Optional[str]
    architecture_analysis: Optional[Dict[str, Any]]

# Pydantic models for structured output
class PersonaInfo(BaseModel):
    name: str = Field(description="Name of the persona/user")
    role: str = Field(description="Role or job title of the persona")
    description: str = Field(description="Description of what this persona does")
    goals: List[str] = Field(description="Primary goals and objectives of this persona")
    interactions: List[str] = Field(description="How this persona interacts with the system")
    technology_preferences: Optional[str] = Field(description="Technology preferences if mentioned")
    tags: List[str] = Field(description="Relevant tags for categorization")

class SystemInfo(BaseModel):
    name: str = Field(description="Name of the system")
    description: str = Field(description="Description of the system's purpose")
    technology: Optional[str] = Field(description="Technology stack if mentioned")
    primary_users: List[str] = Field(description="Primary personas/users who use this system")
    user_goals: List[str] = Field(description="Goals this system helps users achieve")
    tags: List[str] = Field(description="Relevant tags for categorization")

class ContainerInfo(BaseModel):
    name: str = Field(description="Name of the container")
    system: str = Field(description="System this container belongs to")
    description: str = Field(description="Description of the container's purpose")
    technology: Optional[str] = Field(description="Technology stack if mentioned")
    user_interfaces: List[str] = Field(description="User interfaces or APIs this container provides")
    user_experience: Optional[str] = Field(description="User experience considerations")
    tags: List[str] = Field(description="Relevant tags for categorization")

class ComponentInfo(BaseModel):
    name: str = Field(description="Name of the component")
    container: str = Field(description="Container this component belongs to")
    description: str = Field(description="Description of the component's purpose")
    technology: Optional[str] = Field(description="Technology stack if mentioned")
    user_workflows: List[str] = Field(description="User workflows this component supports")
    accessibility: Optional[str] = Field(description="Accessibility considerations for users")
    tags: List[str] = Field(description="Relevant tags for categorization")

class RelationshipInfo(BaseModel):
    source: str = Field(description="Source component/system/container")
    destination: str = Field(description="Destination component/system/container")
    description: str = Field(description="Nature of the interaction")
    technology: Optional[str] = Field(description="Protocol/technology if mentioned")
    relationship_type: str = Field(description="Type of relationship: uses, depends_on, communicates_with")
    user_impact: Optional[str] = Field(description="How this relationship affects user experience")
    user_workflow: Optional[str] = Field(description="User workflow this relationship supports")

class UserExperienceAnalysis(BaseModel):
    personas: List[PersonaInfo]
    user_journeys: List[str] = Field(description="Key user journeys through the system")
    accessibility_features: List[str] = Field(description="Accessibility features and considerations")
    user_goals: List[str] = Field(description="Primary user goals the system addresses")
    pain_points: List[str] = Field(description="Potential user pain points or challenges")

class ArchitectureAnalysis(BaseModel):
    systems: List[SystemInfo]
    containers: List[ContainerInfo]
    components: List[ComponentInfo]
    relationships: List[RelationshipInfo]
    external_systems: List[SystemInfo]
    personas: List[PersonaInfo]
    user_experience: UserExperienceAnalysis
    missing_info: List[str]
    summary: str

# Agent 1: Parse and analyze technical specification
def parse_spec_node(state: C4State) -> C4State:
    """Parse the technical specification to extract C4 architecture elements"""
    print("🔍 Parsing technical specification...")
    
    llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.1)
    parser = JsonOutputParser(pydantic_object=ArchitectureAnalysis)
    
    prompt = f"""
    You are a senior software architect specializing in C4 model diagrams with expertise in user experience and persona analysis. Analyze the following technical specification and extract comprehensive C4 model elements with a focus on user perspective.

    Technical Specification:
    {state["raw_spec"]}

    Your task is to identify and categorize all architectural elements from a USER-CENTRIC perspective:

    1. personas: Identify all user personas who interact with the system
       - Name, role, goals, and how they interact with the system
       - Technology preferences and accessibility needs
       - Primary workflows and pain points

    2. systems: Main software systems that provide value to users
       - Primary users and their goals
       - How the system helps users achieve their objectives

    3. containers: Applications and data stores within each system
       - User interfaces and APIs provided
       - User experience considerations

    4. components: Major components within each container
       - User workflows supported
       - Accessibility features

    5. external systems: Third-party systems, APIs, or services
       - How they impact user experience

    6. relationships: How these elements interact with each other
       - User workflow impact
       - User experience considerations

    7. user_experience: Overall user experience analysis
       - Key user journeys
       - Accessibility features
       - User goals and pain points

    For each element, provide:
    - Clear, descriptive names
    - Purpose and functionality from user perspective
    - Technology stack if mentioned
    - User experience considerations
    - Relevant tags for categorization

    For relationships, identify:
    - Source and destination
    - Nature of interaction
    - Technology/protocol used
    - Type of relationship
    - How it affects user experience

    Return a comprehensive analysis that can be used to generate C4 diagrams at all levels in a JSON format and structured way where each element is a JSON object, with special attention to user personas and experience.
    """
    
    try:
        response = llm.invoke(prompt)
        print(f"Response: {response.content}")
        
        # Parse LLM response into JSON object
        try:
            # First try to parse directly with the parser
            parsed = parser.parse(response.content)
        except Exception as parse_error:
            print(f"Direct parsing failed: {parse_error}")
            # If direct parsing fails, try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    print(f"JSON extracted and parsed successfully")
                except json.JSONDecodeError as json_error:
                    print(f"JSON parsing failed: {json_error}")
                    # If JSON parsing fails, create a basic structure
                    parsed = {
                        "systems": [],
                        "containers": [],
                        "components": [],
                        "relationships": [],
                        "external_systems": [],
                        "personas": [],
                        "user_experience": {
                            "personas": [],
                            "user_journeys": [],
                            "accessibility_features": [],
                            "user_goals": [],
                            "pain_points": []
                        },
                        "missing_info": ["Failed to parse LLM response into valid JSON"],
                        "summary": "Error parsing response"
                    }
            else:
                print("No JSON found in response")
                # No JSON found, create basic structure
                parsed = {
                    "systems": [],
                    "containers": [],
                    "components": [],
                    "relationships": [],
                    "external_systems": [],
                    "personas": [],
                    "user_experience": {
                        "personas": [],
                        "user_journeys": [],
                        "accessibility_features": [],
                        "user_goals": [],
                        "pain_points": []
                    },
                    "missing_info": ["No JSON response found in LLM output"],
                    "summary": "No valid response structure found"
                }
        
        print(f"Parsed: {parsed}")
        
        return {
            **state,
            "systems": parsed.get("systems", []),
            "containers": parsed.get("containers", []),
            "components": parsed.get("components", []),
            "relationships": parsed.get("relationships", []),
            "external_systems": parsed.get("external_systems", []),
            "personas": parsed.get("personas", []),
            "user_experience": parsed.get("user_experience", {}),
            "missing_info": parsed.get("missing_info", []),
            "summary": parsed.get("summary", "Architecture analysis completed"),
            "architecture_analysis": parsed
        }
    except Exception as e:
        print(f"Error parsing specification: {e}")
        return {
            **state,
            "missing_info": [f"Failed to parse specification: {str(e)}"]
        }

# Agent 2: Validate and enhance architecture analysis
def validate_architecture_node(state: C4State) -> C4State:
    """Validate the extracted architecture and identify any gaps or inconsistencies"""
    print("✅ Validating architecture analysis...")
    
    llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.1)
    
    # Prepare current analysis for validation
    current_analysis = {
        "systems": state.get("systems", []),
        "containers": state.get("containers", []),
        "components": state.get("components", []),
        "relationships": state.get("relationships", []),
        "external_systems": state.get("external_systems", []),
        "personas": state.get("personas", []),
        "user_experience": state.get("user_experience", {})
    }
    
    prompt = f"""
    You are an architecture validation expert with expertise in user experience and persona analysis. Review the following C4 architecture analysis and identify:

    1. Missing architectural elements
    2. Inconsistencies in relationships
    3. Unclear boundaries between systems
    4. Missing external dependencies
    5. Opportunities for better organization
    6. Missing or incomplete user personas
    7. Gaps in user experience analysis
    8. Accessibility considerations
    9. User workflow completeness

    Current Analysis:
    {json.dumps(current_analysis, indent=2)}

    Original Specification:
    {state["raw_spec"]}

    Provide recommendations for improvement and identify any critical missing elements, with special focus on user experience and persona completeness.
    """
    
    try:
        response = llm.invoke(prompt)
        
        # Extract recommendations and improvements
        recommendations = response.content
        
        # Update missing info with validation findings
        current_missing = state.get("missing_info", [])
        if "missing" in recommendations.lower() or "gap" in recommendations.lower():
            current_missing.append("Architecture validation identified potential gaps - review recommended")
        
        return {
            **state,
            "missing_info": current_missing,
            "summary": f"{state.get('summary', '')}\n\nValidation: {recommendations[:200]}..."
        }
    except Exception as e:
        print(f"Error validating architecture: {e}")
        return state

# Agent 3: Generate System Context Diagram DSL
def generate_context_dsl_node(state: C4State) -> C4State:
    """Generate Structurizr DSL for System Context Diagram (Level 1)"""
    print("🌐 Generating System Context Diagram DSL...")
    
    llm = ChatOpenAI(model="gpt-4.1", api_key=api_key, temperature=0.1)
    
    systems = state.get("systems", [])
    external_systems = state.get("external_systems", [])
    relationships = state.get("relationships", [])

    print(f"Systems: {systems}")
    print(f"External Systems: {external_systems}")
    print(f"Relationships: {relationships}")
    
    prompt = f"""
    Generate a Structurizr DSL for a System Context Diagram (C4 Level 1) based on this architecture:

    Systems: {json.dumps(systems, indent=2)}
    External Systems: {json.dumps(external_systems, indent=2)}
    Relationships: {json.dumps(relationships, indent=2)}

    Create a complete Structurizr DSL that includes:
    1. Workspace definition
    2. Model with all systems and external systems
    3. Views showing the system context
    4. Proper styling and layout
    5. Clearly identify the systems, containers and external systems.
    6. Containers should be nested inside their systems.
    7. Container views for each system
    8. Proper relationships between containers
    9. Technology information for containers

    Focus on showing:
    - Main systems and their boundaries
    - External systems and APIs
    - High-level relationships between systems
    - Clear system boundaries
    - Containers within each system
    - Container-to-container relationships
    - Technology choices for each container
    - Data flow between containers
    - Check for duplicate relationships among systems and containers and remove them.

    Some Do's and Dont's:
    - Do not use any markup or comments in the DSL code.
    - Do not apply any custom styles 
    - Do not use spaces inside view names
    - Do not add relationship between parent and child entities.
    

   
    Return ONLY the Structurizr DSL code, no explanations without markup. Also make sure it follows the Structurizr DSL syntax while generating the
    DSL code.

    Below is the example of the Structurizr DSL code:
    {example_dsl}
    """
    
    try:
        response = llm.invoke(prompt)
        dsl = response.content.strip()
        
        return {
            **state,
            "dsl_context": dsl
        }
    except Exception as e:
        print(f"Error generating context DSL: {e}")
        return {
            **state,
            "dsl_context": f"// Error generating context DSL: {str(e)}"
        }

# Generate user-centric C4 diagrams with personas
def generate_user_centric_dsl_node(state: C4State) -> C4State:
    """Generate user-centric C4 diagrams with personas and user experience focus"""
    print("👥 Generating user-centric C4 diagrams...")
    
    try:
        # Generate the user-centric DSL
        user_centric_dsl = generate_user_centric_dsl_content(state)
        
        return {
            **state,
            "dsl_user_centric": user_centric_dsl
        }
    except Exception as e:
        print(f"Error generating user-centric DSL: {e}")
        return {
            **state,
            "dsl_user_centric": f"// Error generating user-centric DSL: {str(e)}"
        }

def generate_user_centric_dsl_content(state: C4State) -> str:
    """
    Generate Structurizr DSL that focuses on user experience and personas.
    
    Creates C4 diagrams that emphasize user interactions, workflows,
    and experience considerations alongside technical architecture.
    
    Args:
        state: C4State containing architecture and persona information
        
    Returns:
        str: Structurizr DSL code for user-centric diagrams
    """
    
    personas = state.get("personas", [])
    systems = state.get("systems", [])
    containers = state.get("containers", [])
    relationships = state.get("relationships", [])
    user_experience = state.get("user_experience", {})
    
    if not personas:
        return "// No personas identified in the specification"
    
    dsl_lines = []
    dsl_lines.append("workspace \"User-Centric C4 Architecture\" \"Architecture focused on user experience and personas\" {")
    dsl_lines.append("  model {")
    
    # Add personas first (they are the primary actors)
    for persona in personas:
        name = persona.get("name", "Unknown User")
        role = persona.get("role", "User")
        description = persona.get("description", "")
        
        # Create persona alias
        alias = f"persona_{name.lower().replace(' ', '_').replace('-', '_')}"
        
        line = f"    person \"{name}\" \"{role}\" as {alias}"
        if description:
            line += f" \"{description}\""
        dsl_lines.append(line)
    
    dsl_lines.append("")
    
    # Add systems with user focus
    for system in systems:
        name = system.get("name", "System")
        description = system.get("description", "")
        primary_users = system.get("primary_users", [])
        
        alias = f"system_{name.lower().replace(' ', '_').replace('-', '_')}"
        
        line = f"    softwareSystem \"{name}\" as {alias}"
        if description:
            line += f" \"{description}\""
        dsl_lines.append(line)
        
        # Add containers within systems
        system_containers = [c for c in containers if c.get("system") == name]
        if system_containers:
            dsl_lines.append("    {")
            for container in system_containers:
                c_name = container.get("name", "Container")
                c_desc = container.get("description", "")
                c_tech = container.get("technology", "")
                user_interfaces = container.get("user_interfaces", [])
                
                c_alias = f"container_{c_name.lower().replace(' ', '_').replace('-', '_')}"
                
                line = f"      container \"{c_name}\" as {c_alias}"
                if c_desc and c_tech:
                    line += f" \"{c_desc}\" \"{c_tech}\""
                elif c_desc:
                    line += f" \"{c_desc}\""
                elif c_tech:
                    line += f" \"\" \"{c_tech}\""
                dsl_lines.append(line)
                
                # Add user interface information as notes
                if user_interfaces:
                    dsl_lines.append(f"      note \"User Interfaces: {', '.join(user_interfaces)}\" as note_{c_alias}")
            dsl_lines.append("    }")
    
    dsl_lines.append("")
    
    # Add relationships with user workflow focus
    for rel in relationships:
        source = rel.get("source", "")
        destination = rel.get("destination", "")
        description = rel.get("description", "")
        user_impact = rel.get("user_impact", "")
        user_workflow = rel.get("user_workflow", "")
        
        # Find aliases for source and destination
        source_alias = _find_alias(source, personas, systems, containers)
        dest_alias = _find_alias(destination, personas, systems, containers)
        
        if source_alias and dest_alias:
            line = f"    {source_alias} -> {dest_alias}"
            if description:
                line += f" \"{description}\""
            dsl_lines.append(line)
            
            # Add user workflow notes if available
            if user_workflow:
                dsl_lines.append(f"    note \"User Workflow: {user_workflow}\" as note_{source_alias}_{dest_alias}")
    
    dsl_lines.append("  }")
    
    # Add views focused on user experience
    dsl_lines.append("  views {")
    
    # Persona-focused system context view
    dsl_lines.append("    systemContext * \"User-Centric System Context\" {")
    dsl_lines.append("      include *")
    dsl_lines.append("      autoLayout")
    dsl_lines.append("    }")
    
    # User journey view
    if user_experience.get("user_journeys"):
        dsl_lines.append("    systemContext * \"User Journey View\" {")
        dsl_lines.append("      include *")
        dsl_lines.append("      autoLayout")
        dsl_lines.append("    }")
    
    # Accessibility and UX considerations
    if user_experience.get("accessibility_features"):
        dsl_lines.append("    systemContext * \"Accessibility & UX Features\" {")
        dsl_lines.append("      include *")
        dsl_lines.append("      autoLayout")
        dsl_lines.append("    }")
    
    # Styles for better user experience visualization
    dsl_lines.append("    styles {")
    dsl_lines.append("      element \"Person\" { background #08427b color #ffffff shape Person }")
    dsl_lines.append("      element \"Software System\" { background #1168bd color #ffffff }")
    dsl_lines.append("      element \"Container\" { background #438dd5 color #ffffff }")
    dsl_lines.append("      element \"Note\" { background #f5f5f5 color #000000 }")
    dsl_lines.append("    }")
    
    dsl_lines.append("  }")
    dsl_lines.append("}")
    
    return "\n".join(dsl_lines)

def _find_alias(name: str, personas: List[Dict], systems: List[Dict], containers: List[Dict]) -> Optional[str]:
    """
    Find the alias for a given name across personas, systems, and containers.
    
    Args:
        name: Name to search for
        personas: List of persona dictionaries
        systems: List of system dictionaries
        containers: List of container dictionaries
        
    Returns:
        Optional[str]: Alias if found, None otherwise
    """
    
    # Check personas
    for persona in personas:
        if persona.get("name") == name:
            return f"persona_{name.lower().replace(' ', '_').replace('-', '_')}"
    
    # Check systems
    for system in systems:
        if system.get("name") == name:
            return f"system_{name.lower().replace(' ', '_').replace('-', '_')}"
    
    # Check containers
    for container in containers:
        if container.get("name") == name:
            return f"container_{name.lower().replace(' ', '_').replace('-', '_')}"
    
    return None


def final_review_node(state: C4State) -> C4State:
    """Perform final review and create comprehensive summary"""
    print("📋 Performing final review...")
    
    llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.1)
    
    # Prepare summary of what was generated
    generated_content = {
        "systems_count": len(state.get("systems", [])),
        "containers_count": len(state.get("containers", [])),
        "components_count": len(state.get("components", [])),
        "relationships_count": len(state.get("relationships", [])),
        "external_systems_count": len(state.get("external_systems", [])),
        "personas_count": len(state.get("personas", [])),
        "user_experience_analysis": bool(state.get("user_experience", {})),
        "dsl_generated": {
            "context": bool(state.get("dsl_context")),
            "container": bool(state.get("dsl_container")),
            "component": bool(state.get("dsl_component")),
            "user_centric": bool(state.get("dsl_user_centric"))
        }
    }
    
    prompt = f"""
    Review the C4 architecture generation results and provide a comprehensive summary with focus on user experience:

    Generated Content Summary:
    {json.dumps(generated_content, indent=2)}

    Original Specification:
    {state["raw_spec"][:500]}...

    Provide a summary that includes:
    1. What was successfully identified and generated
    2. Quality assessment of the generated diagrams
    3. User experience and persona analysis completeness
    4. Recommendations for using the generated DSL
    5. User-centric considerations and workflows
    6. Any limitations or areas for improvement

    Keep the summary concise but informative, emphasizing the user perspective.
    """
    
    try:
        response = llm.invoke(prompt)
        final_summary = response.content
        
        return {
            **state,
            "summary": f"{state.get('summary', '')}\n\nFinal Review:\n{final_summary}"
        }
    except Exception as e:
        print(f"Error in final review: {e}")
        return state

# Create the LangGraph workflow
def create_c4_workflow() -> StateGraph:
    """Create the LangGraph workflow for C4 architecture generation with user experience focus"""
    
    workflow = StateGraph(C4State)
    
    # Add nodes
    workflow.add_node("parse_spec", parse_spec_node)
    workflow.add_node("validate_architecture", validate_architecture_node)
    workflow.add_node("generate_context_dsl", generate_context_dsl_node)
    workflow.add_node("generate_user_centric_dsl", generate_user_centric_dsl_node)
    workflow.add_node("final_review", final_review_node)
    
    # Define the workflow
    workflow.set_entry_point("parse_spec")
    workflow.add_edge("parse_spec", "validate_architecture")
    workflow.add_edge("validate_architecture", "generate_context_dsl")
    workflow.add_edge("generate_context_dsl", "generate_user_centric_dsl")
    workflow.add_edge("generate_user_centric_dsl", "final_review")
    workflow.add_edge("final_review", END)
    
    return workflow.compile()

# Main function to generate C4 architecture
def generate_c4_architecture(technical_spec: str) -> Dict[str, Any]:
    """
    Generate C4 architecture diagrams from technical specification
    
    Args:
        technical_spec (str): Technical specification of the system
        
    Returns:
        Dict containing generated DSL code and analysis
    """
    
    print("🚀 Starting C4 Architecture Generation...")
    print("=" * 60)
    
    # Create workflow
    workflow = create_c4_workflow()
    
    # Initialize state
    initial_state = C4State(
        raw_spec=technical_spec,
        systems=None,
        containers=None,
        components=None,
        relationships=None,
        external_systems=None,
        personas=None,
        user_experience=None,
        missing_info=None,
        summary=None,
        dsl_context=None,
        dsl_container=None,
        dsl_context_container=None,
        dsl_component=None,
        dsl_user_centric=None,
        architecture_analysis=None
    )
    
    # Execute workflow
    try:
        result = workflow.invoke(initial_state)
        
        print("✅ C4 Architecture Generation Completed!")
        print("=" * 60)
        
        return {
            "success": True,
            "summary": result.get("summary", "No summary available"),
            "systems": result.get("systems", []),
            "containers": result.get("containers", []),
            "components": result.get("components", []),
            "relationships": result.get("relationships", []),
            "external_systems": result.get("external_systems", []),
            "personas": result.get("personas", []),
            "user_experience": result.get("user_experience", {}),
            "missing_info": result.get("missing_info", []),
            "dsl": {
                "context": result.get("dsl_context"),
                "container": result.get("dsl_container"),
                "context_container": result.get("dsl_context_container"),
                "component": result.get("dsl_component"),
                "user_centric": result.get("dsl_user_centric")
            },
            "architecture_analysis": result.get("architecture_analysis")
        }
        
    except Exception as e:
        print(f"❌ Error in C4 architecture generation: {e}")
        return {
            "success": False,
            "error": str(e),
            "summary": "Generation failed due to an error"
        }

# Utility function to save DSL to files
def save_dsl_files(result: Dict[str, Any], output_dir: str = "generated_c4") -> List[str]:
    """
    Save generated DSL files to disk
    
    Args:
        result: Result from generate_c4_architecture
        output_dir: Directory to save files
        
    Returns:
        List of saved file paths
    """
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    saved_files = []
    
    if result.get("success"):
        dsl = result.get("dsl", {})
        
        # Save context diagram DSL
        if dsl.get("context"):
            context_file = Path(output_dir) / "system_context.dsl"
            with open(context_file, 'w') as f:
                f.write(dsl["context"])
            saved_files.append(str(context_file))
            print(f"💾 Saved System Context DSL: {context_file}")
        
        # Save container diagram DSL
        if dsl.get("container"):
            container_file = Path(output_dir) / "container.dsl"
            with open(container_file, 'w') as f:
                f.write(dsl["container"])
            saved_files.append(str(container_file))
            print(f"💾 Saved Container DSL: {container_file}")
        
        # Save component diagram DSL
        if dsl.get("component"):
            component_file = Path(output_dir) / "component.dsl"
            with open(component_file, 'w') as f:
                f.write(dsl["component"])
            saved_files.append(str(component_file))
            print(f"💾 Saved Component DSL: {component_file}")

        # Save merged context+container DSL
        if dsl.get("context_container"):
            merged_file = Path(output_dir) / "context_container.dsl"
            with open(merged_file, 'w') as f:
                f.write(dsl["context_container"])
            saved_files.append(str(merged_file))
            print(f"💾 Saved Merged Context+Container DSL: {merged_file}")
        
        # Save user-centric DSL
        if dsl.get("user_centric"):
            user_centric_file = Path(output_dir) / "user_centric.dsl"
            with open(user_centric_file, 'w') as f:
                f.write(dsl["user_centric"])
            saved_files.append(str(user_centric_file))
            print(f"💾 Saved User-Centric DSL: {user_centric_file}")
        
        # Save summary and analysis
        summary_file = Path(output_dir) / "architecture_summary.json"
        with open(summary_file, 'w') as f:
            json.dump({
                "summary": result.get("summary"),
                "systems": result.get("systems", []),
                "containers": result.get("containers", []),
                "components": result.get("components", []),
                "relationships": result.get("relationships", []),
                "external_systems": result.get("external_systems", []),
                "personas": result.get("personas", []),
                "user_experience": result.get("user_experience", {}),
                "missing_info": result.get("missing_info", [])
            }, f, indent=2)
        saved_files.append(str(summary_file))
        print(f"💾 Saved Architecture Summary: {summary_file}")
        
        # Save detailed persona and user experience analysis
        if result.get("personas") or result.get("user_experience"):
            persona_file = Path(output_dir) / "user_experience_analysis.json"
            with open(persona_file, 'w') as f:
                json.dump({
                    "personas": result.get("personas", []),
                    "user_experience": result.get("user_experience", {}),
                    "generated_at": datetime.now().isoformat(),
                    "technical_spec": result.get("raw_spec", "")
                }, f, indent=2)
            saved_files.append(str(persona_file))
            print(f"💾 Saved User Experience Analysis: {persona_file}")
    
    return saved_files

# Example usage function
def example_usage():
    """Example usage of the C4 architecture generator"""
    
    # Example technical specification
    spec = """
    The system is a modern e-commerce platform with the following architecture:
    
    1. Frontend System: React-based web application with mobile-responsive design
    2. API Gateway: Node.js service that routes requests to appropriate microservices
    3. User Service: Java Spring Boot service managing user authentication and profiles
    4. Product Service: Python FastAPI service handling product catalog and inventory
    5. Order Service: Go service processing orders and managing order lifecycle
    6. Payment Service: .NET Core service integrating with multiple payment gateways
    7. Notification Service: Node.js service sending emails, SMS, and push notifications
    8. Database Layer: PostgreSQL for user data, MongoDB for products, Redis for caching
    9. Message Queue: Apache Kafka for asynchronous communication between services
    10. External Systems: Payment gateways (Stripe, PayPal), email service (SendGrid), SMS service (Twilio) and also a third party API for product search and recommendations.
    
    The Frontend System communicates with the API Gateway, which routes requests to appropriate microservices.
    Services communicate asynchronously through Kafka for events like order creation and payment processing.
    The Payment Service integrates with external payment gateways and notifies the Notification Service of results.
    All services use the Database Layer for data persistence and Redis for caching frequently accessed data.
    """
    
    print("🔍 Example: E-commerce Platform Architecture")
    print("=" * 60)
    
    # Generate C4 architecture
    result = generate_c4_architecture(spec)
    
    if result.get("success"):
        print(f"\n📊 Architecture Analysis:")
        print(f"- Systems identified: {len(result.get('systems', []))}")
        print(f"- Containers identified: {len(result.get('containers', []))}")
        print(f"- Components identified: {len(result.get('components', []))}")
        print(f"- Relationships identified: {len(result.get('relationships', []))}")
        
        # Save files
        saved_files = save_dsl_files(result)
        print(f"\n💾 Generated {len(saved_files)} files")
        
        # Display summary
        print(f"\n📋 Summary:")
        print(result.get("summary", "No summary available"))
        
    else:
        print(f"❌ Generation failed: {result.get('error')}")

if __name__ == "__main__":
    # Check if API key is available
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set.")
        print("Please set it to use the C4 architecture generator.")
        print("You can set it with: export OPENAI_API_KEY='your-key-here'")
    else:
        example_usage()
