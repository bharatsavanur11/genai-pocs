#!/usr/bin/env python3
"""
Simple demo of the C4 Architecture Diagram Generator

This script demonstrates the basic usage of the C4 generator
with a simple technical specification.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def demo_simple_web_app():
    """Demo with a simple web application specification"""
    print("🚀 C4 Architecture Diagram Generator - Demo")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-key-here'")
        print("Or create a .env file with: OPENAI_API_KEY=your-key-here")
        return False
    
    print("✅ OpenAI API key found")
    
    try:
        # Import the C4 generator
        from c4_with_excel_tech_spec import generate_c4_from_spec
        
        # Define a simple technical specification
        spec = """
        The system is a simple web application with the following components:
        
        1. A web browser (client) that users interact with
        2. A web server that handles HTTP requests and serves HTML pages
        3. A database that stores user data and application information
        4. An external payment gateway API for processing payments
        
        The web browser sends HTTP requests to the web server. The web server 
        processes these requests, retrieves data from the database when needed, 
        and communicates with the payment gateway for payment processing. 
        The web server then sends responses back to the web browser.
        """
        
        print("\n📋 Technical Specification:")
        print("-" * 40)
        print(spec.strip())
        
        print("\n🔄 Generating C4 diagram...")
        print("This may take a few moments...")
        
        # Generate the C4 diagram
        result = generate_c4_from_spec(spec)
        
        # Display results
        print("\n✅ C4 Diagram Generated Successfully!")
        print("=" * 60)
        
        # Summary
        if result.get("summary"):
            print("\n📝 System Summary:")
            print(result["summary"])
        
        # Components
        if result.get("components"):
            print(f"\n🏗️  Components Found ({len(result['components'])}):")
            for i, comp in enumerate(result["components"], 1):
                print(f"  {i}. {comp['name']} ({comp['type']})")
                print(f"     Description: {comp['description']}")
                if comp.get('technology'):
                    print(f"     Technology: {comp['technology']}")
                print()
        
        # Relationships
        if result.get("relationships"):
            print(f"🔗 Relationships Found ({len(result['relationships'])}):")
            for i, rel in enumerate(result["relationships"], 1):
                print(f"  {i}. {rel['source']} → {rel['destination']}")
                print(f"     Interaction: {rel['description']}")
                if rel.get('technology'):
                    print(f"     Technology: {rel['technology']}")
                print()
        
        # DSL Code
        if result.get("dsl"):
            print("📊 Generated Structurizr DSL:")
            print("-" * 40)
            print(result["dsl"])
            
            # Save to file
            filename = "demo_web_app.dsl"
            with open(filename, 'w') as f:
                f.write(result["dsl"])
            print(f"\n💾 DSL saved to: {filename}")
        
        # Missing information
        if result.get("missing_info") and result["missing_info"] != None:
            print("\n⚠️  Missing Information:")
            print(result["missing_info"])
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Use the generated DSL with Structurizr or other C4 tools")
        print("2. Try the web interface: streamlit run c4_with_excel_tech_spec.py")
        print("3. Run more examples: python example_usage.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed all dependencies:")
        print("pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        print("Check your OpenAI API key and internet connection")
        return False

def main():
    """Main demo function"""
    try:
        success = demo_simple_web_app()
        if success:
            print("\n✅ Demo completed successfully!")
            return 0
        else:
            print("\n❌ Demo failed!")
            return 1
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
