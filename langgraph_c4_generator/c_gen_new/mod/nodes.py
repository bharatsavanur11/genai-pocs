import json
import re
from typing import Any, Dict, List

from langchain_core.output_parsers import JsonOutputParser

from .config import get_llm
from .state import C4State, ArchitectureAnalysis
from .merge_dsl import build_unified_workspace_dsl


def parse_spec_node(state: C4State) -> C4State:
    print("🔍 Parsing technical specification...")
    llm = get_llm()
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

        try:
            parsed = parser.parse(response.content)
        except Exception as parse_error:
            print(f"Direct parsing failed: {parse_error}")
            json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                except json.JSONDecodeError:
                    parsed = {"systems": [], "containers": [], "components": [], "relationships": [], "external_systems": [], "missing_info": ["Failed to parse LLM response into valid JSON"], "summary": "Error parsing response"}
            else:
                parsed = {"systems": [], "containers": [], "components": [], "relationships": [], "external_systems": [], "missing_info": ["No JSON response found in LLM output"], "summary": "No valid response structure found"}

        return {**state, "systems": parsed.get("systems", []), "containers": parsed.get("containers", []), "components": parsed.get("components", []), "relationships": parsed.get("relationships", []), "external_systems": parsed.get("external_systems", []), "missing_info": parsed.get("missing_info", []), "summary": parsed.get("summary", "Architecture analysis completed"), "architecture_analysis": parsed}
    except Exception as e:
        print(f"Error parsing specification: {e}")
        return {**state, "missing_info": [f"Failed to parse specification: {str(e)}"]}


def validate_architecture_node(state: C4State) -> C4State:
    print("✅ Validating architecture analysis...")
    llm = get_llm()
    current_analysis = {"systems": state.get("systems", []), "containers": state.get("containers", []), "components": state.get("components", []), "relationships": state.get("relationships", []), "external_systems": state.get("external_systems", [])}
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
        recommendations = response.content
        current_missing = state.get("missing_info", [])
        if "missing" in recommendations.lower() or "gap" in recommendations.lower():
            current_missing.append("Architecture validation identified potential gaps - review recommended")
        return {**state, "missing_info": current_missing, "summary": f"{state.get('summary', '')}\n\nValidation: {recommendations[:200]}..."}
    except Exception as e:
        print(f"Error validating architecture: {e}")
        return state


def generate_context_dsl_node(state: C4State) -> C4State:
    print("🌐 Generating System Context Diagram DSL...")
    llm = get_llm()
    systems = state.get("systems", [])
    external_systems = state.get("external_systems", [])
    relationships = state.get("relationships", [])
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

    Focus on showing:
    - Main systems and their boundaries
    - External systems and APIs
    - High-level relationships between systems
    - Clear system boundaries

    Return ONLY the Structurizr DSL code, no explanations.
    """
    try:
        response = llm.invoke(prompt)
        return {**state, "dsl_context": response.content.strip()}
    except Exception as e:
        print(f"Error generating context DSL: {e}")
        return {**state, "dsl_context": f"// Error generating context DSL: {str(e)}"}


def generate_container_dsl_node(state: C4State) -> C4State:
    print("📦 Generating Container Diagram DSL...")
    llm = get_llm()
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
    3. Container views for each system
    4. Proper relationships between containers
    5. Technology information for containers

    Focus on showing:
    - Containers within each system
    - Container-to-container relationships
    - Technology choices for each container
    - Data flow between containers

    Return ONLY the Structurizr DSL code, no explanations.
    """
    try:
        response = llm.invoke(prompt)
        return {**state, "dsl_container": response.content.strip()}
    except Exception as e:
        print(f"Error generating container DSL: {e}")
        return {**state, "dsl_container": f"// Error generating container DSL: {str(e)}"}


def generate_component_dsl_node(state: C4State) -> C4State:
    print("🔧 Generating Component Diagram DSL...")
    llm = get_llm()
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
        return {**state, "dsl_component": response.content.strip()}
    except Exception as e:
        print(f"Error generating component DSL: {e}")
        return {**state, "dsl_component": f"// Error generating component DSL: {str(e)}"}


def final_review_node(state: C4State) -> C4State:
    print("📋 Performing final review...")
    llm = get_llm()
    generated_content = {"systems_count": len(state.get("systems", [])), "containers_count": len(state.get("containers", [])), "components_count": len(state.get("components", [])), "relationships_count": len(state.get("relationships", [])), "external_systems_count": len(state.get("external_systems", [])), "dsl_generated": {"context": bool(state.get("dsl_context")), "container": bool(state.get("dsl_container")), "component": bool(state.get("dsl_component"))}}
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
        return {**state, "summary": f"{state.get('summary', '')}\n\nFinal Review:\n{final_summary}"}
    except Exception as e:
        print(f"Error in final review: {e}")
        return state


def merge_context_and_container_node(state: C4State) -> C4State:
    return {**state, "dsl_context_container": build_unified_workspace_dsl(state)}


