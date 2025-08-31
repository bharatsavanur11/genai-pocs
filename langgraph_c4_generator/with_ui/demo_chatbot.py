#!/usr/bin/env python3
"""
Demo script for the C4 Architecture Generator Chatbot

This script demonstrates the chatbot functionality programmatically,
showing how it processes inputs and generates C4 diagrams.
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def demo_content_filtering():
    """Demonstrate content filtering functionality"""
    print("🔍 Demo: Content Filtering")
    print("=" * 50)
    
    # Example inputs with mixed content
    test_inputs = [
        "I need a web application with React frontend and Node.js backend",
        "How are you doing today? The weather is nice.",
        "The system should use PostgreSQL database and Redis for caching",
        "What's for lunch? I'm thinking about pizza.",
        "We need to integrate with Stripe for payments and SendGrid for emails"
    ]
    
    print("Testing content filtering with various inputs:\n")
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"Input {i}: {input_text}")
        
        # Simulate content filtering (in real chatbot, this uses AI)
        if any(keyword in input_text.lower() for keyword in [
            'web application', 'react', 'node.js', 'database', 'postgresql', 
            'redis', 'stripe', 'sendgrid', 'system', 'integration'
        ]):
            print("✅ Relevant technical content detected")
            print(f"   Extracted: {input_text}")
        else:
            print("❌ No relevant technical content")
        
        print()
    
    print("=" * 50)

def demo_context_building():
    """Demonstrate context building functionality"""
    print("🧩 Demo: Context Building")
    print("=" * 50)
    
    # Simulate conversation flow
    conversation_steps = [
        "I need a web application with React frontend",
        "The backend should be Node.js with Express",
        "Add PostgreSQL database for data storage",
        "Include Redis for session management",
        "Integrate with Stripe for payment processing"
    ]
    
    print("Building technical specification incrementally:\n")
    
    context = ""
    for i, step in enumerate(conversation_steps, 1):
        print(f"Step {i}: {step}")
        
        if context:
            context += f"\n\nAdditional Context:\n{step}"
        else:
            context = step
        
        print(f"   Current context length: {len(context)} characters")
        print(f"   Context preview: {context[:100]}...")
        print()
    
    print("Final combined specification:")
    print("-" * 30)
    print(context)
    print("=" * 50)

def demo_c4_generation():
    """Demonstrate C4 generation functionality"""
    print("🏗️ Demo: C4 Architecture Generation")
    print("=" * 50)
    
    # Check if we can import the C4 generator
    try:
        from c4_generator_new import generate_c4_architecture
        
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
        10. External Systems: Payment gateways (Stripe, PayPal), email service (SendGrid), SMS service (Twilio)
        """
        
        print("Generating C4 architecture from specification...")
        print("(This may take a moment depending on API response time)\n")
        
        # Generate C4 architecture
        result = generate_c4_architecture(spec)
        
        if result.get("success"):
            print("✅ C4 Architecture generated successfully!")
            print(f"   Systems identified: {len(result.get('systems', []))}")
            print(f"   Containers identified: {len(result.get('containers', []))}")
            print(f"   Components identified: {len(result.get('components', []))}")
            print(f"   Relationships identified: {len(result.get('relationships', []))}")
            
            # Show summary
            summary = result.get("summary", "No summary available")
            print(f"\n📋 Summary: {summary[:200]}...")
            
            # Show DSL availability
            dsl = result.get("dsl", {})
            print(f"\n📄 Generated DSL files:")
            print(f"   System Context: {'✅' if dsl.get('context') else '❌'}")
            print(f"   Container: {'✅' if dsl.get('container') else '❌'}")
            print(f"   Component: {'✅' if dsl.get('component') else '❌'}")
            print(f"   Unified: {'✅' if dsl.get('context_container') else '❌'}")
            
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
    
    except ImportError as e:
        print(f"❌ Could not import C4 generator: {e}")
        print("Make sure you're in the correct directory and dependencies are installed")
    except Exception as e:
        print(f"❌ Error during C4 generation: {e}")
    
    print("=" * 50)

def demo_chatbot_workflow():
    """Demonstrate the complete chatbot workflow"""
    print("🤖 Demo: Complete Chatbot Workflow")
    print("=" * 50)
    
    print("This demonstrates how the chatbot processes a conversation:\n")
    
    # Simulate a conversation
    conversation = [
        {
            "user": "I need a simple web application",
            "bot_response": "✅ Added to technical specification:\n- Simple web application",
            "context_update": "Simple web application"
        },
        {
            "user": "It should have a React frontend and Node.js backend",
            "bot_response": "✅ Added to technical specification:\n- React frontend\n- Node.js backend",
            "context_update": "Simple web application\n\nAdditional Context:\n- React frontend\n- Node.js backend"
        },
        {
            "user": "Add a PostgreSQL database",
            "bot_response": "✅ Added to technical specification:\n- PostgreSQL database",
            "context_update": "Simple web application\n\nAdditional Context:\n- React frontend\n- Node.js backend\n\nAdditional Context:\n- PostgreSQL database"
        }
    ]
    
    for i, step in enumerate(conversation, 1):
        print(f"Step {i}:")
        print(f"   User: {step['user']}")
        print(f"   Bot: {step['bot_response']}")
        print(f"   Context length: {len(step['context_update'])} characters")
        print()
    
    print("After this conversation, the chatbot would:")
    print("1. ✅ Filter out any non-technical content")
    print("2. 🧩 Build a comprehensive technical specification")
    print("3. 🏗️ Generate C4 architecture diagrams")
    print("4. 📊 Display results in multiple diagram levels")
    print("5. 💾 Allow saving of generated DSL files")
    
    print("=" * 50)

def main():
    """Run all demo functions"""
    print("🚀 C4 Architecture Generator Chatbot Demo")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("Some demos may not work without API access\n")
    else:
        print("✅ OpenAI API key detected\n")
    
    # Run demos
    demo_content_filtering()
    print()
    
    demo_context_building()
    print()
    
    demo_chatbot_workflow()
    print()
    
    # Only run C4 generation if API key is available
    if api_key:
        demo_c4_generation()
    else:
        print("🏗️ Demo: C4 Architecture Generation")
        print("=" * 50)
        print("⚠️  Skipping C4 generation demo - no API key available")
        print("Set OPENAI_API_KEY to see this demo in action")
        print("=" * 50)
    
    print("\n🎉 Demo completed!")
    print("\nTo run the full chatbot interface:")
    print("  streamlit run c4_chatbot_ui.py")
    print("\nOr use the launcher:")
    print("  python run_chatbot.py")

if __name__ == "__main__":
    main()
