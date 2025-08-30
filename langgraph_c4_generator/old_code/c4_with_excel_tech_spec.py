from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List, Optional, Union
import re
import uuid
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import sys
import os
# Load environment variables
load_dotenv()

# Get API key from environment variable
if not api_key:
    print("Warning: OPENAI_API_KEY environment variable not set. Please set it to use OpenAI services.")
    api_key = "dummy-key"  # This will cause an error but allows the script to run for testing

# Define the state
class C4State(Dict[str, Any]):
    raw_spec: str
    excel_data: Optional[Dict[str, Any]]
    components: Optional[List[Dict[str, str]]]
    relationships: Optional[List[Dict[str, str]]]
    missing_info: Optional[List[str]]
    summary: Optional[str]
    dsl: Optional[str]
    architecture_level: Optional[str]  # context, container, component, code

# Agent 1: Parse technical specification
def parse_spec_node(state: C4State) -> C4State:
    """Parse the technical specification to extract C4 components and relationships"""
    print("Parse Spec Node:", state)
    llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.1)
    
    raw_spec = state["raw_spec"]
    excel_data = state.get("excel_data", {})
    
    # Enhanced prompt for better C4 extraction
    prompt = f"""
    You are a software architect specializing in C4 model diagrams. Analyze the following technical specification and extract C4 model elements.

    Technical Specification:
    {raw_spec}

    {f'Additional Excel Data: {json.dumps(excel_data, indent=2)}' if excel_data else ''}

    Extract the following information and return as a JSON object:

    1. COMPONENTS: List all software components, systems, containers, or external systems mentioned
       - name: Component name
       - type: One of [softwareSystem, container, component, person, externalSystem]
       - description: Clear description of purpose/functionality
       - technology: Technology stack if mentioned (optional)
       - tags: Relevant tags like "database", "api", "ui", "service" (optional)

    2. RELATIONSHIPS: List all interactions between components
       - source: Source component name
       - destination: Target component name
       - description: Nature of the interaction
       - technology: Protocol/technology if mentioned (optional)

    3. MISSING_INFO: List any unclear or missing information that would help create a better diagram

    4. ARCHITECTURE_LEVEL: Determine the most appropriate C4 level [context, container, component, code]

    Return ONLY valid JSON in this exact format:
    {{
        "components": [
            {{"name": "Component1", "type": "component", "description": "Description", "technology": "tech", "tags": ["tag1"]}}
        ],
        "relationships": [
            {{"source": "Component1", "destination": "Component2", "description": "Interaction", "technology": "protocol"}}
        ],
        "missing_info": ["Missing detail 1", "Missing detail 2"],
        "architecture_level": "component"
    }}
    """
    
    try:
        response = llm.invoke(prompt).content
        # Clean the response to extract JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return {
                **state,
                "components": parsed.get("components", []),
                "relationships": parsed.get("relationships", []),
                "missing_info": parsed.get("missing_info", []),
                "architecture_level": parsed.get("architecture_level", "component")
            }
        else:
            return {
                **state,
                "missing_info": ["Failed to parse LLM response. Please check the specification format."]
            }
    except Exception as e:
        return {
            **state,
            "missing_info": [f"Error parsing specification: {str(e)}"]
        }

# Agent 2: Request missing information
def request_info_node(state: C4State) -> C4State:
    """Generate a request for missing information"""
    print("Request Info Node:", state)
    if not state.get("missing_info"):
        return {**state, "missing_info": None}
    
    missing = state["missing_info"]
    llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.3)
    
    prompt = f"""
    The following information is missing from the technical specification:
    {', '.join(missing)}
    
    Generate a clear, professional request for the user to provide this missing information.
    Make it specific and actionable. Return only the request text.
    """
    
    response = llm.invoke(prompt).content
    return {**state, "missing_info": response}

# Agent 3: Summarize requirements
def summarize_node(state: C4State) -> C4State:
    """Create a summary of the system requirements"""
    print("Summarize Node:", state)
    llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.2)
    
    components = state.get("components", [])
    relationships = state.get("relationships", [])
    
    prompt = f"""
    Create a concise, professional summary of the system architecture based on these C4 components and relationships.
    
    Components:
    {json.dumps(components, indent=2)}
    
    Relationships:
    {json.dumps(relationships, indent=2)}
    
    Write a 2-3 sentence summary that describes the overall system purpose and key architectural decisions.
    """
    
    summary = llm.invoke(prompt).content
    return {**state, "summary": summary}

# Agent 4: Generate Structurizr DSL
def generate_dsl_node(state: C4State) -> C4State:
    """Generate Structurizr DSL code for the C4 diagram"""
    print("Generate DSL Node:", state)
    components = state.get("components", [])
    relationships = state.get("relationships", [])
    architecture_level = state.get("architecture_level", "component")
    
    # Start building the DSL
    dsl_lines = [
        "workspace {",
        "    name \"C4 Architecture Diagram\"",
        "    description \"Generated from technical specification\"",
        "",
        "    model {"
    ]
    
    # Define components based on their type
    component_vars = {}
    for comp in components:
        name = comp.get("name", "").replace(" ", "_").replace("-", "_").lower()
        comp_type = comp.get("type", "component")
        description = comp.get("description", "No description provided")
        technology = comp.get("technology", "")
        tags = comp.get("tags", [])
        
        # Create component variable name
        var_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        if var_name[0].isdigit():
            var_name = f"comp_{var_name}"
        
        component_vars[comp.get("name")] = var_name
        
        # Generate component definition based on type
        if comp_type == "softwareSystem":
            dsl_lines.append(f'        {var_name} = softwareSystem "{comp.get("name")}" "{description}"')
        elif comp_type == "container":
            dsl_lines.append(f'        {var_name} = container "{comp.get("name")}" "{description}"')
        elif comp_type == "component":
            dsl_lines.append(f'        {var_name} = component "{comp.get("name")}" "{description}"')
        elif comp_type == "person":
            dsl_lines.append(f'        {var_name} = person "{comp.get("name")}" "{description}"')
        elif comp_type == "externalSystem":
            dsl_lines.append(f'        {var_name} = softwareSystem "{comp.get("name")}" "{description}"')
        else:
            dsl_lines.append(f'        {var_name} = component "{comp.get("name")}" "{description}"')
        
        # Add technology if specified
        if technology:
            dsl_lines.append(f'        {var_name}.technology = "{technology}"')
        
        # Add tags if specified
        if tags:
            dsl_lines.append(f'        {var_name}.tags = "{", ".join(tags)}"')
        
        dsl_lines.append("")
    
    # Define relationships
    for rel in relationships:
        source = rel.get("source", "")
        destination = rel.get("destination", "")
        description = rel.get("description", "Interacts with")
        technology = rel.get("technology", "")
        
        if source in component_vars and destination in component_vars:
            source_var = component_vars[source]
            dest_var = component_vars[destination]
            
            rel_line = f'        {source_var} -> {dest_var} "{description}"'
            if technology:
                rel_line += f' "{technology}"'
            dsl_lines.append(rel_line)
    
    # Close model section
    dsl_lines.extend([
        "    }",
        "",
        "    views {"
    ])
    
    # Add appropriate views based on architecture level
    if architecture_level == "context":
        dsl_lines.extend([
            '        systemContext system "SystemContext" "System Context Diagram" {',
            "            include *",
            "        }"
        ])
    elif architecture_level == "container":
        dsl_lines.extend([
            '        container system "Containers" "Container Diagram" {',
            "            include *",
            "        }"
        ])
    else:  # component or code level
        dsl_lines.extend([
            '        component system "Components" "Component Diagram" {',
            "            include *",
            "        }"
        ])
    
    # Add additional useful views
    dsl_lines.extend([
        "",
        "        # Additional views for better understanding",
        '        styles {',
        '            element "component" {',
        '                shape "Component"',
        '                background "#1168BD"',
        '                color "#ffffff"',
        '            }',
        '            element "container" {',
        '                shape "Container"',
        '                background "#438DD5"',
        '                color "#ffffff"',
        '            }',
        '            element "softwareSystem" {',
        '                shape "SoftwareSystem"',
        '                background "#999999"',
        '                color "#ffffff"',
        '            }',
        '            element "person" {',
        '                shape "Person"',
        '                background "#08427B"',
        '                color "#ffffff"',
        '            }',
        '        }',
        "    }",
        "}"
    ])
    
    dsl_code = "\n".join(dsl_lines)
    return {**state, "dsl": dsl_code}

# Excel processing function
def process_excel_file(file_path: str) -> Dict[str, Any]:
    """Process Excel file to extract technical specifications"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path, sheet_name=None)
        
        excel_data = {}
        for sheet_name, sheet_df in df.items():
            # Convert DataFrame to structured data
            sheet_data = {
                "headers": sheet_df.columns.tolist(),
                "rows": sheet_df.values.tolist(),
                "summary": f"Sheet '{sheet_name}' contains {len(sheet_df)} rows with columns: {', '.join(sheet_df.columns)}"
            }
            excel_data[sheet_name] = sheet_data
        
        return excel_data
    except Exception as e:
        return {"error": f"Failed to process Excel file: {str(e)}"}

# Build the LangGraph workflow
def build_c4_workflow():
    """Build and return the C4 generation workflow"""
    graph = StateGraph(C4State)
    
    # Add nodes
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
    
    return graph.compile()

# Main execution function
def generate_c4_from_spec(technical_spec: str, excel_file_path: str = None) -> Dict[str, Any]:
    """
    Generate C4 diagram from technical specification
    
    Args:
        technical_spec: Technical specification text
        excel_file_path: Optional path to Excel file with additional data
    
    Returns:
        Dictionary containing the generated C4 diagram and metadata
    """
    # Process Excel file if provided
    excel_data = {}
    if excel_file_path and os.path.exists(excel_file_path):
        excel_data = process_excel_file(excel_file_path)
    
    # Initialize state
    initial_state = C4State({
        "raw_spec": technical_spec,
        "excel_data": excel_data,
        "components": None,
        "relationships": None,
        "missing_info": None,
        "summary": None,
        "dsl": None,
        "architecture_level": None
    })
    
    # Build and run workflow
    app = build_c4_workflow()
    
    # Execute the workflow
    final_state = None
    for step in app.stream(initial_state):
        final_state = step
        print(f"Step: {step}")
    
    return final_state

# Streamlit interface
def main():
    st.title("C4 Architecture Diagram Generator")
    st.write("Generate C4 model diagrams from technical specifications using LangGraph")
    
    # Input section
    st.header("Input Technical Specification")
    tech_spec = st.text_area(
        "Enter your technical specification:",
        height=200,
        placeholder="Describe your system architecture, components, and relationships..."
    )
    
    # Excel file upload
    st.header("Additional Data (Optional)")
    uploaded_file = st.file_uploader(
        "Upload Excel file with additional specifications:",
        type=['xlsx', 'xls']
    )
    
    excel_file_path = None
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with open(f"temp_{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        excel_file_path = f"temp_{uploaded_file.name}"
        st.success(f"Uploaded: {uploaded_file.name}")
    
    # Generate button
    if st.button("Generate C4 Diagram") and tech_spec:
        with st.spinner("Generating C4 diagram..."):
            try:
                result = generate_c4_from_spec(tech_spec, excel_file_path)
                
                # Display results
                st.header("Generated C4 Diagram")
                
                # Summary
                if result.get("summary"):
                    st.subheader("System Summary")
                    st.write(result["summary"])
                
                # Components
                if result.get("components"):
                    st.subheader("Identified Components")
                    for comp in result["components"]:
                        st.write(f"**{comp['name']}** ({comp['type']}): {comp['description']}")
                
                # Relationships
                if result.get("relationships"):
                    st.subheader("Component Relationships")
                    for rel in result["relationships"]:
                        st.write(f"**{rel['source']}** → **{rel['destination']}**: {rel['description']}")
                
                # DSL Code
                if result.get("dsl"):
                    st.subheader("Structurizr DSL Code")
                    st.code(result["dsl"], language="dsl")
                    
                    # Download button for DSL
                    st.download_button(
                        label="Download DSL File",
                        data=result["dsl"],
                        file_name="c4_architecture.dsl",
                        mime="text/plain"
                    )
                
                # Missing information
                if result.get("missing_info") and result["missing_info"] != None:
                    st.warning("Missing Information")
                    st.write(result["missing_info"])
                
            except Exception as e:
                st.error(f"Error generating diagram: {str(e)}")
            finally:
                # Clean up temporary file
                if excel_file_path and os.path.exists(excel_file_path):
                    os.remove(excel_file_path)
    
    elif not tech_spec:
        st.warning("Please enter a technical specification to generate the diagram.")

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        # Command line usage
        spec_file = sys.argv[1]
        with open(spec_file, 'r') as f:
            spec_content = f.read()
        
        result = generate_c4_from_spec(spec_content)
        print("Generated C4 Diagram:")
        print("=" * 50)
        print("Summary:", result.get("summary"))
        print("\nComponents:", len(result.get("components", [])))
        print("\nRelationships:", len(result.get("relationships", [])))
        print("\nDSL Code:")
        print(result.get("dsl", ""))
    else:
        # Run Streamlit app
        import sys
        if 'streamlit' in sys.modules:
            main()
        else:
            print("Run with 'streamlit run c4_with_excel_tech_spec.py' for the web interface")
            print("Or provide a spec file as argument for command line usage") 