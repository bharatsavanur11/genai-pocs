#!/usr/bin/env python3
"""
Example usage of the C4 Architecture Diagram Generator

This script demonstrates how to use the C4 generator with different types of
technical specifications.
"""

from c4_with_excel_tech_spec import generate_c4_from_spec
import os

def example_1_simple_web_app():
    """Example 1: Simple web application"""
    print("=" * 60)
    print("EXAMPLE 1: Simple Web Application")
    print("=" * 60)
    
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
    
    result = generate_c4_from_spec(spec)
    
    print(f"Summary: {result.get('summary', 'No summary')}")
    print(f"Components found: {len(result.get('components', []))}")
    print(f"Relationships found: {len(result.get('relationships', []))}")
    
    if result.get('dsl'):
        print("\nGenerated DSL:")
        print(result['dsl'])
    
    return result

def example_2_microservices_architecture():
    """Example 2: Microservices architecture"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Microservices Architecture")
    print("=" * 60)
    
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
    
    result = generate_c4_from_spec(spec)
    
    print(f"Summary: {result.get('summary', 'No summary')}")
    print(f"Components found: {len(result.get('components', []))}")
    print(f"Relationships found: {len(result.get('relationships', []))}")
    
    if result.get('dsl'):
        print("\nGenerated DSL:")
        print(result['dsl'])
    
    return result

def example_3_data_pipeline():
    """Example 3: Data pipeline system"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Data Pipeline System")
    print("=" * 60)
    
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
    
    result = generate_c4_from_spec(spec)
    
    print(f"Summary: {result.get('summary', 'No summary')}")
    print(f"Components found: {len(result.get('components', []))}")
    print(f"Relationships found: {len(result.get('relationships', []))}")
    
    if result.get('dsl'):
        print("\nGenerated DSL:")
        print(result['dsl'])
    
    return result

def save_dsl_to_file(dsl_content: str, filename: str):
    """Save DSL content to a file"""
    with open(filename, 'w') as f:
        f.write(dsl_content)
    print(f"DSL saved to {filename}")

def main():
    """Run all examples and save results"""
    print("C4 Architecture Diagram Generator - Examples")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("Please set it to use OpenAI services.")
        print("You can set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    try:
        # Run examples
        result1 = example_1_simple_web_app()
        result2 = example_2_microservices_architecture()
        result3 = example_3_data_pipeline()
        
        # Save DSL files
        if result1.get('dsl'):
            save_dsl_to_file(result1['dsl'], 'simple_web_app.dsl')
        
        if result2.get('dsl'):
            save_dsl_to_file(result2['dsl'], 'microservices_architecture.dsl')
        
        if result3.get('dsl'):
            save_dsl_to_file(result3['dsl'], 'data_pipeline.dsl')
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("Generated DSL files:")
        print("- simple_web_app.dsl")
        print("- microservices_architecture.dsl")
        print("- data_pipeline.dsl")
        print("\nYou can now use these DSL files with Structurizr or other C4 tools.")
        
    except Exception as e:
        print(f"Error running examples: {str(e)}")
        print("Make sure you have set the OPENAI_API_KEY environment variable")

if __name__ == "__main__":
    main()
