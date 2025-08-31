#!/usr/bin/env python3
"""
C4 Architecture Generator using LangGraph

This module provides a comprehensive solution for generating C4 architecture diagrams
from technical specifications using LangGraph workflow. It can generate:

1. System Context Diagrams (Level 1)
2. Container Diagrams (Level 2) 
3. Component Diagrams (Level 3)

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




# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
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
    missing_info: Optional[List[str]]
    summary: Optional[str]
    dsl_context: Optional[str]
    dsl_container: Optional[str]
    dsl_component: Optional[str]
    dsl_context_container: Optional[str]
    architecture_analysis: Optional[Dict[str, Any]]

# Pydantic models for structured output
class SystemInfo(BaseModel):
    name: str = Field(description="Name of the system")
    description: str = Field(description="Description of the system's purpose")
    technology: Optional[str] = Field(description="Technology stack if mentioned")
    tags: List[str] = Field(description="Relevant tags for categorization")

class ContainerInfo(BaseModel):
    name: str = Field(description="Name of the container")
    system: str = Field(description="System this container belongs to")
    description: str = Field(description="Description of the container's purpose")
    technology: Optional[str] = Field(description="Technology stack if mentioned")
    tags: List[str] = Field(description="Relevant tags for categorization")

class ComponentInfo(BaseModel):
    name: str = Field(description="Name of the component")
    container: str = Field(description="Container this component belongs to")
    description: str = Field(description="Description of the component's purpose")
    technology: Optional[str] = Field(description="Technology stack if mentioned")
    tags: List[str] = Field(description="Relevant tags for categorization")

class RelationshipInfo(BaseModel):
    source: str = Field(description="Source component/system/container")
    destination: str = Field(description="Destination component/system/container")
    description: str = Field(description="Nature of the interaction")
    technology: Optional[str] = Field(description="Protocol/technology if mentioned")
    relationship_type: str = Field(description="Type of relationship: uses, depends_on, communicates_with")

class ArchitectureAnalysis(BaseModel):
    systems: List[SystemInfo]
    containers: List[ContainerInfo]
    components: List[ComponentInfo]
    relationships: List[RelationshipInfo]
    external_systems: List[SystemInfo]
    missing_info: List[str]
    summary: str

# Agent 1: Parse and analyze technical specification
def parse_spec_node(state: C4State) -> C4State:
    """Parse the technical specification to extract C4 architecture elements"""
    print("🔍 Parsing technical specification...")
    
    llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.1)
    parser = JsonOutputParser(pydantic_object=ArchitectureAnalysis)
    
    prompt = f"""
    You are a senior software architect specializing in C4 model diagrams. Analyze the following technical specification and extract comprehensive C4 model elements.

    Technical Specification:
    {state["raw_spec"]}

    Your task is to identify and categorize all architectural elements:

    1. systems: Main software systems that provide value to users
    2. containers: Applications and data stores within each system
    3. components: Major components within each container
    4. external systems: Third-party systems, APIs, or services
    5. relationships: How these elements interact with each other

    For each element, provide:
    - Clear, descriptive names
    - Purpose and functionality
    - Technology stack if mentioned
    - Relevant tags for categorization

    For relationships, identify:
    - Source and destination
    - Nature of interaction
    - Technology/protocol used
    - Type of relationship

    Return a comprehensive analysis that can be used to generate C4 diagrams at all levels in a JSON format and structred way where each element is a JSON object.
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
        "external_systems": state.get("external_systems", [])
    }
    
    prompt = f"""
    You are an architecture validation expert. Review the following C4 architecture analysis and identify:

    1. Missing architectural elements
    2. Inconsistencies in relationships
    3. Unclear boundaries between systems
    4. Missing external dependencies
    5. Opportunities for better organization

    Current Analysis:
    {json.dumps(current_analysis, indent=2)}

    Original Specification:
    {state["raw_spec"]}

    Provide recommendations for improvement and identify any critical missing elements.
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
    5. Container views for each system
    6. Proper relationships between containers
    7. Technology information for containers

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

# Agent 4: Generate Container Diagram DSL
def generate_container_dsl_node(state: C4State) -> C4State:
    """Generate Structurizr DSL for Container Diagram (Level 2)"""
    print("📦 Generating Container Diagram DSL...")
    
    llm = ChatOpenAI(model="gpt-4.1", api_key=api_key, temperature=0.1)
    
    systems = state.get("systems", [])
    containers = state.get("containers", [])
    relationships = state.get("relationships", [])
    
    prompt = f"""
    Generate a Structurizr DSL for Container Diagrams (C4 Level 2) based on this architecture:

    Systems: {json.dumps(systems, indent=2)}
    Containers: {json.dumps(containers, indent=2)}
    Relationships: {json.dumps(relationships, indent=2)}

    Create Structurizr DSL that includes:
    1. Workspace definition     
    2. Model with systems and their containers
    3. Views showing the system context
    4. Container views for each system
    5. Proper relationships between containers
    6. Technology information for containers

    Focus on showing:
    - Containers within each system
    - Container-to-container relationships
    - Technology choices for each container
    - Data flow between containers

    Return ONLY the Structurizr DSL code, no explanations. 
    """
    
    try:
        response = llm.invoke(prompt)
        dsl = response.content.strip()
        
        return {
            **state,
            "dsl_container": dsl
        }
    except Exception as e:
        print(f"Error generating container DSL: {e}")
        return {
            **state,
            "dsl_container": f"// Error generating container DSL: {str(e)}"
        }

# Agent 4.5: Merge Context and Container DSLs
def merge_context_and_container_node(state: C4State) -> C4State:
    """Generate a single valid Structurizr DSL where containers are nested inside their systems."""
    print("🧩 Building unified Structurizr DSL (systems + containers)...")

    systems = state.get("systems", []) or []
    containers = state.get("containers", []) or []
    external_systems = state.get("external_systems", []) or []
    relationships = state.get("relationships", []) or []

    if not systems and not containers and not external_systems:
        return {**state, "dsl_context_container": "// No architecture elements available to build DSL"}

    def make_alias(name: str) -> str:
        base = re.sub(r"[^A-Za-z0-9_]", "_", name.strip())
        base = re.sub(r"_+", "_", base)
        return base[:60] if base else "Element"

    # Build alias maps
    system_alias: Dict[str, str] = {}
    container_alias: Dict[str, str] = {}
    external_alias: Dict[str, str] = {}

    # Assign aliases for systems
    for sys_obj in systems:
        name = sys_obj.get("name") or sys_obj.get("title") or "System"
        alias = make_alias(name)
        # Ensure uniqueness
        i = 2
        orig = alias
        while alias in system_alias.values():
            alias = f"{orig}_{i}"
            i += 1
        system_alias[name] = alias

    # Assign aliases for external systems
    for ext in external_systems:
        name = ext.get("name") or "ExternalSystem"
        alias = make_alias(name)
        i = 2
        orig = alias
        while alias in external_alias.values() or alias in system_alias.values():
            alias = f"{orig}_{i}"
            i += 1
        external_alias[name] = alias

    # Assign aliases for containers (names may not be unique across systems)
    for cont in containers:
        name = cont.get("name") or "Container"
        sys_name = cont.get("system") or cont.get("belongs_to") or next((s.get("name") for s in systems), None)
        key = (sys_name or "_global_", name)
        alias = make_alias(f"{system_alias.get(sys_name, sys_name or 'Sys')}_{name}")
        i = 2
        orig = alias
        while alias in container_alias.values() or alias in system_alias.values() or alias in external_alias.values():
            alias = f"{orig}_{i}"
            i += 1
        container_alias[key] = alias

    # Start building DSL
    dsl_lines: List[str] = []
    dsl_lines.append("workspace \"C4 Workspace\" \"Unified context+container view\" {")
    dsl_lines.append("  model {")

    # Software Systems (internal)
    for sys_obj in systems:
        name = sys_obj.get("name") or "System"
        desc = sys_obj.get("description") or sys_obj.get("purpose") or ""
        tech = sys_obj.get("technology") or ""
        alias = system_alias[name]
        header = f"    softwareSystem \"{name}\" as {alias}"
        dsl_lines.append(header + " {")
        if desc:
            dsl_lines.append(f"      description \"{desc}\"")
        if tech:
            dsl_lines.append(f"      technology \"{tech}\"")

        # Containers belonging to this system
        for cont in [c for c in containers if (c.get("system") or c.get("belongs_to")) == name]:
            c_name = cont.get("name") or "Container"
            c_desc = cont.get("description") or cont.get("purpose") or ""
            c_tech = cont.get("technology") or ""
            c_alias = container_alias.get((name, c_name)) or make_alias(f"{alias}_{c_name}")
            line = f"      container \"{c_name}\" as {c_alias}"
            if c_desc and c_tech:
                line += f" \"{c_desc}\" \"{c_tech}\""
            elif c_desc:
                line += f" \"{c_desc}\""
            elif c_tech:
                line += f" \"\" \"{c_tech}\""
            dsl_lines.append(line)
        dsl_lines.append("    }")

    # External systems
    for ext in external_systems:
        name = ext.get("name") or "ExternalSystem"
        desc = ext.get("description") or ext.get("purpose") or ""
        tech = ext.get("technology") or ""
        alias = external_alias[name]
        line = f"    softwareSystem \"{name}\" as {alias} <<External>>"
        dsl_lines.append(line + " {")
        if desc:
            dsl_lines.append(f"      description \"{desc}\"")
        if tech:
            dsl_lines.append(f"      technology \"{tech}\"")
        dsl_lines.append("    }")

    # Relationships
    def rel_line(src_alias: str, dst_alias: str, rel: Dict[str, Any]) -> str:
        desc = rel.get("description") or rel.get("interaction") or ""
        tech = rel.get("technology") or ""
        if desc and tech:
            return f"    {src_alias} -> {dst_alias} \"{desc}\" \"{tech}\""
        if desc:
            return f"    {src_alias} -> {dst_alias} \"{desc}\""
        if tech:
            return f"    {src_alias} -> {dst_alias} \"\" \"{tech}\""
        return f"    {src_alias} -> {dst_alias}"

    # Build name to alias lookup
    name_to_alias: Dict[str, str] = {**{k: v for k, v in system_alias.items()}, **{k: v for k, v in external_alias.items()}}
    # Prefer container alias when name matches a container uniquely
    for (sys_name, cont_name), alias in container_alias.items():
        # if cont name unique across all containers, map by name for convenience
        count = sum(1 for (s, c) in container_alias.keys() if c == cont_name)
        if count == 1:
            name_to_alias[cont_name] = alias

    # Relationship lines
    for rel in relationships:
        src_name = rel.get("source") or rel.get("from")
        dst_name = rel.get("destination") or rel.get("to")
        if not src_name or not dst_name:
            continue

        # Try exact name matches first
        src_alias = name_to_alias.get(src_name)
        dst_alias = name_to_alias.get(dst_name)

        # If not found, try container lookup assuming unique names or first system
        if not src_alias:
            # Try any container with that name
            for (s, c), a in container_alias.items():
                if c == src_name:
                    src_alias = a
                    break
        if not dst_alias:
            for (s, c), a in container_alias.items():
                if c == dst_name:
                    dst_alias = a
                    break

        # If still missing, skip this relationship
        if not src_alias or not dst_alias:
            continue

        dsl_lines.append(rel_line(src_alias, dst_alias, rel))

    dsl_lines.append("  }")  # end model

    # Views: create one systemContext per internal system, and container view per internal system
    dsl_lines.append("  views {")
    for sys_obj in systems:
        name = sys_obj.get("name") or "System"
        alias = system_alias[name]
        dsl_lines.append(f"    systemContext {alias} \"{name} - System Context\" {{")
        dsl_lines.append("      include *")
        dsl_lines.append("      autolayout lr")
        dsl_lines.append("    }")

        dsl_lines.append(f"    container {alias} \"{name} - Containers\" {{")
        dsl_lines.append("      include *")
        dsl_lines.append("      autolayout lr")
        dsl_lines.append("    }")

    # Basic styles
    dsl_lines.append("    styles {")
    dsl_lines.append("      element \"Software System\" { background #1168bd color #ffffff }")
    dsl_lines.append("      element \"Container\" { background #438dd5 color #ffffff }")
    dsl_lines.append("      element \"Component\" { background #85bbf0 color #000000 }")
    dsl_lines.append("      element \"External\" { background #999999 color #ffffff }")
    dsl_lines.append("    }")
    dsl_lines.append("  }")  # end views
    dsl_lines.append("}")  # end workspace

    merged_dsl = "\n".join(dsl_lines)
    return {**state, "dsl_context_container": merged_dsl}

# Agent 5: Generate Component Diagram DSL
def generate_component_dsl_node(state: C4State) -> C4State:
    """Generate Structurizr DSL for Component Diagram (Level 3)"""
    print("🔧 Generating Component Diagram DSL...")
    
    llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.1)
    
    containers = state.get("containers", [])
    components = state.get("components", [])
    relationships = state.get("relationships", [])
    
    prompt = f"""
    Generate a Structurizr DSL for Component Diagrams (C4 Level 3) based on this architecture:

    Containers: {json.dumps(containers, indent=2)}
    Components: {json.dumps(components, indent=2)}
    Relationships: {json.dumps(relationships, indent=2)}

    Create Structurizr DSL that includes:
    1. Workspace definition
    2. Model with containers and their components
    3. Component views for each container
    4. Detailed component relationships
    5. Technology and implementation details

    Focus on showing:
    - Components within each container
    - Component-to-component relationships
    - Detailed interaction patterns
    - Technology implementation details

    Return ONLY the Structurizr DSL code, no explanations.
    """
    
    try:
        response = llm.invoke(prompt)
        dsl = response.content.strip()
        
        return {
            **state,
            "dsl_component": dsl
        }
    except Exception as e:
        print(f"Error generating component DSL: {e}")
        return {
            **state,
            "dsl_component": f"// Error generating component DSL: {str(e)}"
        }

# Agent 6: Final review and summary
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
        "dsl_generated": {
            "context": bool(state.get("dsl_context")),
            "container": bool(state.get("dsl_container")),
            "component": bool(state.get("dsl_component"))
        }
    }
    
    prompt = f"""
    Review the C4 architecture generation results and provide a comprehensive summary:

    Generated Content Summary:
    {json.dumps(generated_content, indent=2)}

    Original Specification:
    {state["raw_spec"][:500]}...

    Provide a summary that includes:
    1. What was successfully identified and generated
    2. Quality assessment of the generated diagrams
    3. Recommendations for using the generated DSL
    4. Any limitations or areas for improvement

    Keep the summary concise but informative.
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
    """Create the LangGraph workflow for C4 architecture generation"""
    
    workflow = StateGraph(C4State)
    
    # Add nodes
    workflow.add_node("parse_spec", parse_spec_node)
    workflow.add_node("validate_architecture", validate_architecture_node)
    workflow.add_node("generate_context_dsl", generate_context_dsl_node)
   # workflow.add_node("generate_container_dsl", generate_container_dsl_node)
 #   workflow.add_node("merge_context_and_container", merge_context_and_container_node)
  #  workflow.add_node("generate_component_dsl", generate_component_dsl_node)
    workflow.add_node("final_review", final_review_node)
    
    # Define the workflow
    workflow.set_entry_point("parse_spec")
    workflow.add_edge("parse_spec", "validate_architecture")
    workflow.add_edge("validate_architecture", "generate_context_dsl")
    workflow.add_edge("generate_context_dsl", "final_review")
   # workflow.add_edge("generate_container_dsl", "merge_context_and_container")
   # workflow.add_edge("merge_context_and_container", "final_review")
    # workflow.add_edge("generate_container_dsl", "generate_component_dsl")
    #workflow.add_edge("generate_component_dsl", "final_review")
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
        missing_info=None,
        summary=None,
        dsl_context=None,
        dsl_container=None,
        dsl_context_container=None,
        dsl_component=None,
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
            "missing_info": result.get("missing_info", []),
            "dsl": {
                "context": result.get("dsl_context"),
                "container": result.get("dsl_container"),
                "context_container": result.get("dsl_context_container"),
                "component": result.get("dsl_component")
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
                "missing_info": result.get("missing_info", [])
            }, f, indent=2)
        saved_files.append(str(summary_file))
        print(f"💾 Saved Architecture Summary: {summary_file}")
    
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
