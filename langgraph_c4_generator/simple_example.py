#!/usr/bin/env python3
"""
Simple example demonstrating the C4 Architecture Diagram Generator structure

This script shows how the generator works without requiring an OpenAI API key.
It demonstrates the workflow structure and state management.
"""

from c4_with_excel_tech_spec import C4State, build_c4_workflow
import json

def demonstrate_workflow_structure():
    """Demonstrate the workflow structure without API calls"""
    print("🔧 C4 Architecture Diagram Generator - Workflow Demo")
    print("=" * 60)
    
    # Create a sample state
    sample_state = C4State({
        "raw_spec": "Sample technical specification for demonstration",
        "excel_data": {},
        "components": [
            {
                "name": "Web Server",
                "type": "component",
                "description": "Handles HTTP requests and serves web pages",
                "technology": "Node.js",
                "tags": ["web", "server"]
            },
            {
                "name": "Database",
                "type": "component",
                "description": "Stores application data",
                "technology": "PostgreSQL",
                "tags": ["database", "storage"]
            },
            {
                "name": "Payment Gateway",
                "type": "externalSystem",
                "description": "Processes payment transactions",
                "technology": "Stripe API",
                "tags": ["external", "payment"]
            }
        ],
        "relationships": [
            {
                "source": "Web Server",
                "destination": "Database",
                "description": "Queries and updates data",
                "technology": "SQL"
            },
            {
                "source": "Web Server",
                "destination": "Payment Gateway",
                "description": "Sends payment requests",
                "technology": "HTTPS"
            }
        ],
        "missing_info": None,
        "summary": "A web application with server, database, and payment integration",
        "dsl": None,
        "architecture_level": "component"
    })
    
    print("📋 Sample State Created:")
    print(f"  - Raw Spec: {sample_state['raw_spec']}")
    print(f"  - Components: {len(sample_state['components'])}")
    print(f"  - Relationships: {len(sample_state['relationships'])}")
    print(f"  - Architecture Level: {sample_state['architecture_level']}")
    
    # Build the workflow
    print("\n🏗️  Building Workflow...")
    workflow = build_c4_workflow()
    print("✅ Workflow built successfully!")
    
    # Show workflow structure
    print("\n📊 Workflow Structure:")
    print("  START → parse_spec → [conditional] → request_info OR summarize")
    print("  request_info → END")
    print("  summarize → generate_dsl → END")
    
    # Demonstrate state transitions
    print("\n🔄 State Transition Demo:")
    
    # Parse spec node (simulated)
    print("  1. Parse Spec Node:")
    print(f"     Input: {sample_state['raw_spec'][:50]}...")
    print(f"     Output: {len(sample_state['components'])} components, {len(sample_state['relationships'])} relationships")
    
    # Summarize node (simulated)
    print("  2. Summarize Node:")
    print(f"     Input: Components and relationships")
    print(f"     Output: {sample_state['summary']}")
    
    # Generate DSL node (simulated)
    print("  3. Generate DSL Node:")
    print(f"     Input: Components, relationships, and architecture level")
    print(f"     Output: Structurizr DSL code")
    
    return sample_state

def demonstrate_dsl_generation():
    """Demonstrate DSL generation with sample data"""
    print("\n📊 DSL Generation Demo:")
    print("-" * 40)
    
    # Sample components and relationships
    components = [
        {
            "name": "Web Server",
            "type": "component",
            "description": "Handles HTTP requests and serves web pages",
            "technology": "Node.js",
            "tags": ["web", "server"]
        },
        {
            "name": "Database",
            "type": "component",
            "description": "Stores application data",
            "technology": "PostgreSQL",
            "tags": ["database", "storage"]
        }
    ]
    
    relationships = [
        {
            "source": "Web Server",
            "destination": "Database",
            "description": "Queries and updates data",
            "technology": "SQL"
        }
    ]
    
    # Generate DSL manually (simulating the generate_dsl_node)
    dsl_lines = [
        "workspace {",
        '    name "C4 Architecture Diagram"',
        '    description "Generated from technical specification"',
        "",
        "    model {",
        '        web_server = component "Web Server" "Handles HTTP requests and serves web pages"',
        '        database = component "Database" "Stores application data"',
        "",
        '        web_server -> database "Queries and updates data"',
        "    }",
        "",
        "    views {",
        '        component system "Components" "Component Diagram" {',
        "            include *",
        "        }",
        "    }",
        "}"
    ]
    
    dsl_code = "\n".join(dsl_lines)
    
    print("Generated DSL:")
    print(dsl_code)
    
    # Save to file
    filename = "demo_dsl.dsl"
    with open(filename, 'w') as f:
        f.write(dsl_code)
    print(f"\n💾 DSL saved to: {filename}")
    
    return dsl_code

def show_usage_examples():
    """Show different usage examples"""
    print("\n📚 Usage Examples:")
    print("=" * 60)
    
    examples = [
        {
            "name": "Web Interface",
            "command": "streamlit run c4_with_excel_tech_spec.py",
            "description": "Interactive web application for generating C4 diagrams"
        },
        {
            "name": "Command Line",
            "command": "python3 c4_with_excel_tech_spec.py spec_file.txt",
            "description": "Generate diagrams from specification files"
        },
        {
            "name": "Programmatic",
            "command": "from c4_with_excel_tech_spec import generate_c4_from_spec",
            "description": "Use as a Python library in your own scripts"
        },
        {
            "name": "Examples",
            "command": "python3 example_usage.py",
            "description": "Run comprehensive examples with different architectures"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']}")
        print(f"   Command: {example['command']}")
        print(f"   Description: {example['description']}")
        print()
    
    print("🔑 Note: To use with real API calls, set your OpenAI API key:")
    print("   export OPENAI_API_KEY='your-key-here'")

def main():
    """Main demonstration function"""
    try:
        # Demonstrate workflow structure
        sample_state = demonstrate_workflow_structure()
        
        # Demonstrate DSL generation
        dsl_code = demonstrate_dsl_generation()
        
        # Show usage examples
        show_usage_examples()
        
        print("\n🎉 Demo completed successfully!")
        print("\nThe C4 Architecture Diagram Generator is ready to use!")
        print("Set your OpenAI API key to generate real diagrams from specifications.")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
