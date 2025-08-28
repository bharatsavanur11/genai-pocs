#!/usr/bin/env python3
"""
Demo script for the C4 Architecture Generator

This script demonstrates how to use the LangGraph-based C4 generator
with different types of technical specifications.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import the C4 generator
sys.path.append(str(Path(__file__).parent.parent))

from c_gen_new.c4_generator_new import generate_c4_architecture, save_dsl_files

def demo_simple_web_app():
    """Demo 1: Simple web application"""
    print("=" * 80)
    print("DEMO 1: Simple Web Application")
    print("=" * 80)
    
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
    
    print("📝 Technical Specification:")
    print(spec)
    print("\n🚀 Generating C4 Architecture...")
    
    result = generate_c4_architecture(spec)
    
    if result.get("success"):
        print(f"\n✅ Generation successful!")
        print(f"📊 Systems identified: {len(result.get('systems', []))}")
        print(f"📦 Containers identified: {len(result.get('containers', []))}")
        print(f"🔧 Components identified: {len(result.get('components', []))}")
        print(f"🔗 Relationships identified: {len(result.get('relationships', []))}")
        
        # Save files
        output_dir = "demo_outputs/simple_web_app"
        saved_files = save_dsl_files(result, output_dir)
        
        print(f"\n💾 Generated {len(saved_files)} files in {output_dir}")
        
        # Show summary
        print(f"\n📋 Summary:")
        summary = result.get("summary", "No summary available")
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        return result
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return None

def demo_microservices_architecture():
    """Demo 2: Microservices architecture"""
    print("\n" + "=" * 80)
    print("DEMO 2: Microservices Architecture")
    print("=" * 80)
    
    spec = """
    The system is a microservices-based e-commerce platform with the following services:
    
    1. User Service: Manages user authentication, profiles, and preferences
    2. Product Service: Handles product catalog, inventory, and pricing
    3. Order Service: Processes orders, manages order lifecycle
    4. Payment Service: Handles payment processing and transactions
    5. Notification Service: Sends emails, SMS, and push notifications
    6. API Gateway: Routes requests to appropriate services
    7. Message Queue: Handles asynchronous communication between services
    8. Database Cluster: Stores data for all services
    
    The API Gateway receives requests from clients and routes them to appropriate services.
    Services communicate with each other through the Message Queue for asynchronous operations.
    Each service has its own database within the Database Cluster. The Notification Service
    is triggered by events from other services to send notifications to users.
    """
    
    print("📝 Technical Specification:")
    print(spec)
    print("\n🚀 Generating C4 Architecture...")
    
    result = generate_c4_architecture(spec)
    
    if result.get("success"):
        print(f"\n✅ Generation successful!")
        print(f"📊 Systems identified: {len(result.get('systems', []))}")
        print(f"📦 Containers identified: {len(result.get('containers', []))}")
        print(f"🔧 Components identified: {len(result.get('components', []))}")
        print(f"🔗 Relationships identified: {len(result.get('relationships', []))}")
        
        # Save files2
        output_dir = "demo_outputs/microservices"
        saved_files = save_dsl_files(result, output_dir)
        
        print(f"\n💾 Generated {len(saved_files)} files in {output_dir}")
        
        # Show summary
        print(f"\n📋 Summary:")
        summary = result.get("summary", "No summary available")
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        return result
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return None

def demo_data_pipeline():
    """Demo 3: Data pipeline system"""
    print("\n" + "=" * 80)
    print("DEMO 3: Data Pipeline System")
    print("=" * 80)
    
    spec = """
    The system is a data processing pipeline that collects, processes, and analyzes data:
    
    1. Data Sources: Multiple external APIs and databases that provide raw data
    2. Data Collector: Service that pulls data from various sources
    3. Data Processor: Service that cleans, transforms, and enriches data
    4. Data Warehouse: Centralized storage for processed data
    5. Analytics Engine: Service that runs queries and generates reports
    6. Dashboard: Web interface for viewing analytics and reports
    7. Alert Service: Monitors data quality and sends alerts when issues are detected
    
    The Data Collector continuously pulls data from Data Sources and sends it to the Data Processor.
    The Data Processor cleans and transforms the data before storing it in the Data Warehouse.
    The Analytics Engine queries the Data Warehouse to generate insights and reports.
    The Dashboard displays these insights to users. The Alert Service monitors the entire pipeline
    and sends notifications when data quality issues or failures are detected.
    """
    
    print("📝 Technical Specification:")
    print(spec)
    print("\n🚀 Generating C4 Architecture...")
    
    result = generate_c4_architecture(spec)
    
    if result.get("success"):
        print(f"\n✅ Generation successful!")
        print(f"📊 Systems identified: {len(result.get('systems', []))}")
        print(f"📦 Containers identified: {len(result.get('containers', []))}")
        print(f"🔧 Components identified: {len(result.get('components', []))}")
        print(f"🔗 Relationships identified: {len(result.get('relationships', []))}")
        
        # Save files
        output_dir = "demo_outputs/data_pipeline"
        saved_files = save_dsl_files(result, output_dir)
        
        print(f"\n💾 Generated {len(saved_files)} files in {output_dir}")
        
        # Show summary
        print(f"\n📋 Summary:")
        summary = result.get("summary", "No summary available")
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        return result
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return None

def demo_custom_specification():
    """Demo 4: Custom technical specification from user"""
    print("\n" + "=" * 80)
    print("DEMO 4: Custom Technical Specification")
    print("=" * 80)
    
    print("Please provide your technical specification:")
    print("(Press Enter twice to finish)")
    
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    spec = "\n".join(lines[:-1])  # Remove the last empty line
    
    if not spec.strip():
        print("No specification provided. Using default example.")
        spec = """
        The system is a simple REST API service with:
        1. API Gateway for request routing
        2. Authentication Service for user verification
        3. Business Logic Service for core functionality
        4. Database for data persistence
        5. External logging service for monitoring
        """
    
    print("\n📝 Your Technical Specification:")
    print(spec)
    print("\n🚀 Generating C4 Architecture...")
    
    result = generate_c4_architecture(spec)
    
    if result.get("success"):
        print(f"\n✅ Generation successful!")
        print(f"📊 Systems identified: {len(result.get('systems', []))}")
        print(f"📦 Containers identified: {len(result.get('containers', []))}")
        print(f"🔧 Components identified: {len(result.get('components', []))}")
        print(f"🔗 Relationships identified: {len(result.get('relationships', []))}")
        
        # Save files
        output_dir = "demo_outputs/custom_spec"
        saved_files = save_dsl_files(result, output_dir)
        
        print(f"\n💾 Generated {len(saved_files)} files in {output_dir}")
        
        # Show summary
        print(f"\n📋 Summary:")
        summary = result.get("summary", "No summary available")
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        return result
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return None

def main():
    """Run the demo application"""
    print("🚀 C4 Architecture Generator - Demo Application")
    print("=" * 80)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set.")
        print("Please set it to use the C4 architecture generator.")
        print("You can set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    print("Available demos:")
    print("1. Simple Web Application")
    print("2. Microservices Architecture")
    print("3. Data Pipeline System")
    print("4. Custom Technical Specification")
    print("5. Run all demos")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nSelect a demo (0-5): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                demo_simple_web_app()
            elif choice == "2":
                demo_microservices_architecture()
            elif choice == "3":
                demo_data_pipeline()
            elif choice == "4":
                demo_custom_specification()
            elif choice == "5":
                print("\n🔄 Running all demos...")
                demo_simple_web_app()
                demo_microservices_architecture()
                demo_data_pipeline()
                print("\n✅ All demos completed!")
            else:
                print("❌ Invalid choice. Please select 0-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
