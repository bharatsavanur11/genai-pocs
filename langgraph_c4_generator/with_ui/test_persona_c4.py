#!/usr/bin/env python3
"""
Test script for the updated C4 generator with persona and user experience information.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from c4_generator_new import generate_c4_architecture, save_dsl_files

def test_persona_c4_generation():
    """Test C4 generation with persona-focused technical specification"""
    
    # Test technical specification with user personas and experience
    test_spec = """
    The system is a modern e-commerce platform designed for multiple user types:
    
    Primary Users:
    1. Customer (End User): Wants to browse products, make purchases, and track orders
    2. Store Manager: Manages inventory, views sales reports, and handles customer service
    3. System Administrator: Monitors system health, manages user accounts, and configures settings
    
    System Architecture:
    - Frontend System: React-based web application with mobile-responsive design
    - API Gateway: Node.js service that routes requests to appropriate microservices
    - User Service: Java Spring Boot service managing user authentication and profiles
    - Product Service: Python FastAPI service handling product catalog and inventory
    - Order Service: Go service processing orders and managing order lifecycle
    - Payment Service: .NET Core service integrating with multiple payment gateways
    - Notification Service: Node.js service sending emails, SMS, and push notifications
    - Database Layer: PostgreSQL for user data, MongoDB for products, Redis for caching
    - Message Queue: Apache Kafka for asynchronous communication between services
    
    User Workflows:
    - Customer: Browse → Select → Add to Cart → Checkout → Payment → Order Confirmation
    - Store Manager: Login → Dashboard → Inventory Management → Sales Reports → Customer Service
    - System Admin: Login → System Monitoring → User Management → Configuration → Maintenance
    
    Accessibility Features:
    - Screen reader support
    - Keyboard navigation
    - High contrast mode
    - Mobile responsive design
    - Multi-language support
    
    External Systems: Payment gateways (Stripe, PayPal), email service (SendGrid), SMS service (Twilio)
    """
    
    print("🧪 Testing C4 Generation with Persona Information")
    print("=" * 60)
    
    try:
        # Generate C4 architecture
        result = generate_c4_architecture(test_spec)
        
        if result.get("success"):
            print("✅ C4 Generation Successful!")
            print(f"📊 Summary: {result.get('summary', 'No summary')}")
            print(f"🏗️  Systems: {len(result.get('systems', []))}")
            print(f"📦 Containers: {len(result.get('containers', []))}")
            print(f"🔧 Components: {len(result.get('components', []))}")
            print(f"🔗 Relationships: {len(result.get('relationships', []))}")
            print(f"👥 Personas: {len(result.get('personas', []))}")
            print(f"🎯 User Experience: {bool(result.get('user_experience', {}))}")
            
            # Display persona information
            personas = result.get("personas", [])
            if personas:
                print("\n👥 Identified Personas:")
                for i, persona in enumerate(personas, 1):
                    print(f"  {i}. {persona.get('name', 'Unknown')} - {persona.get('role', 'User')}")
                    print(f"     Goals: {', '.join(persona.get('goals', []))}")
                    print(f"     Interactions: {', '.join(persona.get('interactions', []))}")
            
            # Display user experience analysis
            user_experience = result.get("user_experience", {})
            if user_experience:
                print("\n🎯 User Experience Analysis:")
                print(f"  User Journeys: {len(user_experience.get('user_journeys', []))}")
                print(f"  Accessibility Features: {len(user_experience.get('accessibility_features', []))}")
                print(f"  User Goals: {len(user_experience.get('user_goals', []))}")
                print(f"  Pain Points: {len(user_experience.get('pain_points', []))}")
            
            # Check DSL generation
            dsl = result.get("dsl", {})
            print(f"\n📝 DSL Generated:")
            print(f"  Context: {bool(dsl.get('context'))}")
            print(f"  Container: {bool(dsl.get('container'))}")
            print(f"  Component: {bool(dsl.get('component'))}")
            print(f"  User-Centric: {bool(dsl.get('user_centric'))}")
            
            # Save files
            print("\n💾 Saving generated files...")
            saved_files = save_dsl_files(result, "test_output")
            print(f"✅ Saved {len(saved_files)} files:")
            for file_path in saved_files:
                print(f"  - {file_path}")
                
        else:
            print("❌ C4 Generation Failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running this test.")
        sys.exit(1)
    
    test_persona_c4_generation()
