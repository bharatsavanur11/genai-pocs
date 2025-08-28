#!/usr/bin/env python3
"""
Simple Example - C4 Architecture Generator

This script demonstrates the basic usage of the C4 generator
with a minimal technical specification.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Add parent directory to path to import the C4 generator
sys.path.append(str(Path(__file__).parent.parent))

def simple_example():
    """Run a simple example of C4 architecture generation"""
    
    print("🚀 Simple C4 Architecture Generation Example")
    print("=" * 60)
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set.")
        print("Please set it to use the C4 architecture generator.")
        print("You can set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    try:
        # Import the C4 generator
        from c_gen_new.c4_generator_new import generate_c4_architecture, save_dsl_files
        
        # Define a simple technical specification
        spec = """
        The system is a basic web application with the following components:
        
        1. Web Browser: Users interact with the application through their web browser
        2. Web Server: A Node.js server that handles HTTP requests and serves web pages
        3. Database: A PostgreSQL database that stores user data and application information
        4. External API: A third-party payment service API for processing payments
        
        The web browser sends HTTP requests to the web server. The web server processes 
        these requests, retrieves or stores data in the database as needed, and 
        communicates with the external payment API when payment processing is required. 
        The web server then sends responses back to the web browser.
        """
        
        print("📝 Technical Specification:")
        print(spec)
        print("\n🚀 Generating C4 Architecture...")
        
        # Generate the C4 architecture
        result = generate_c4_architecture(spec)
        
        if result.get("success"):
            print(f"\n✅ Generation successful!")
            
            # Display summary of what was generated
            print(f"\n📊 Architecture Analysis:")
            print(f"- Systems identified: {len(result.get('systems', []))}")
            print(f"- Containers identified: {len(result.get('containers', []))}")
            print(f"- Components identified: {len(result.get('components', []))}")
            print(f"- Relationships identified: {len(result.get('relationships', []))}")
            print(f"- External systems identified: {len(result.get('external_systems', []))}")
            
            # Save the generated files
            output_dir = "simple_example_output"
            saved_files = save_dsl_files(result, output_dir)
            
            print(f"\n💾 Generated {len(saved_files)} files in '{output_dir}' directory:")
            for file_path in saved_files:
                print(f"  - {Path(file_path).name}")
            
            # Display the summary
            print(f"\n📋 Summary:")
            summary = result.get("summary", "No summary available")
            if len(summary) > 300:
                print(summary[:300] + "...")
                print("(See the full summary in the generated JSON file)")
            else:
                print(summary)
            
            # Show a sample of the generated DSL
            dsl = result.get("dsl", {})
            if dsl.get("context"):
                print(f"\n🌐 Sample System Context DSL:")
                context_dsl = dsl["context"]
                lines = context_dsl.split('\n')[:10]  # Show first 10 lines
                for line in lines:
                    print(f"  {line}")
                if len(context_dsl.split('\n')) > 10:
                    print("  ...")
            
            print(f"\n🎉 Example completed successfully!")
            print(f"Check the '{output_dir}' directory for all generated files.")
            
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed all dependencies:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check the error details and try again.")

def show_usage_info():
    """Show usage information and next steps"""
    print("\n" + "=" * 60)
    print("📚 USAGE INFORMATION")
    print("=" * 60)
    
    print("\n🎯 What was generated:")
    print("1. System Context Diagram (Level 1) - High-level system overview")
    print("2. Container Diagram (Level 2) - Container-level architecture")
    print("3. Component Diagram (Level 3) - Detailed component view")
    print("4. Architecture Summary - JSON file with all extracted information")
    
    print("\n🔧 Next steps:")
    print("1. View the generated DSL files in the output directory")
    print("2. Use Structurizr or other C4 tools to visualize the diagrams")
    print("3. Modify the technical specification and run again")
    print("4. Try the interactive demo: python demo_c4_generator.py")
    
    print("\n📖 For more information:")
    print("- Read the README.md file")
    print("- Check the QUICK_START.md guide")
    print("- Run the test script: python test_installation.py")

if __name__ == "__main__":
    # Run the simple example
    simple_example()
    
    # Show usage information
    show_usage_info()
