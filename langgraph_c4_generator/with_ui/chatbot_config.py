#!/usr/bin/env python3
"""
Configuration file for the C4 Architecture Generator Chatbot

This file contains configurable settings for the chatbot functionality.
"""

import os
from typing import Dict, Any

# OpenAI Configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))

# Content Filtering Configuration
CONTENT_FILTER_PROMPT = """
You are a technical specification filter. Analyze the following text and extract ONLY content that is relevant to software/system architecture, technical requirements, or system design.

Text to analyze:
{text}

Return ONLY the relevant technical content. Remove:
- Personal conversations
- Non-technical discussions
- Irrelevant questions or comments
- General chat content
- Anything not related to system architecture or technical specifications

If the text contains no relevant technical content, return "NO_RELEVANT_CONTENT".

Return the filtered content:
"""

TECH_SPEC_EXTRACTION_PROMPT = """
You are a technical architect. Extract technical specification information from the following text.
Focus on:
- System components and architecture
- Technology choices
- Data flows and relationships
- External integrations
- System boundaries and containers
- Any architectural decisions or patterns

User input:
{text}

Return ONLY the technical specification content in a clear, structured format.
If this is additional context to an existing spec, format it as additional requirements.
"""

CONTEXT_SUMMARIZATION_PROMPT = """
Summarize the following technical specification while preserving all important architectural details:

{combined_context}

Create a concise but comprehensive summary that includes:
- All system components
- Key relationships
- Technology choices
- External integrations
- Important architectural decisions

Keep the summary under {max_length} characters.
"""

# Application Configuration
APP_TITLE = "C4 Architecture Generator Chatbot"
APP_ICON = "🏗️"
MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "8000"))
AUTO_GENERATE_THRESHOLD = int(os.getenv("AUTO_GENERATE_THRESHOLD", "100"))

# UI Configuration
DEFAULT_OUTPUT_DIR = os.getenv("DEFAULT_OUTPUT_DIR", "generated_c4")
SIDEBAR_EXPANDED = os.getenv("SIDEBAR_EXPANDED", "True").lower() == "true"
LAYOUT_WIDE = os.getenv("LAYOUT_WIDE", "True").lower() == "true"

# Example Specifications
EXAMPLE_SPECIFICATIONS = [
    {
        "title": "E-commerce Platform",
        "description": "Modern e-commerce system with microservices architecture",
        "spec": """
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
    },
    {
        "title": "Banking System",
        "description": "Core banking system with security and compliance",
        "spec": """
        Core Banking System Architecture:
        
        1. Customer Portal: Angular-based web application for customer interactions
        2. Mobile App: React Native mobile application for iOS and Android
        3. Core Banking Engine: Java Spring Boot service handling core banking operations
        4. Transaction Service: Go service managing financial transactions and settlements
        5. Security Service: .NET Core service handling authentication, authorization, and encryption
        6. Compliance Engine: Python service for regulatory compliance and reporting
        7. Risk Management: Java service for credit risk assessment and monitoring
        8. Data Warehouse: Snowflake for analytical data and reporting
        9. Message Bus: Apache Kafka for event-driven architecture
        10. External Integrations: SWIFT for international transfers, credit bureaus, regulatory systems
        """
    },
    {
        "title": "Healthcare Platform",
        "description": "Patient management and telemedicine system",
        "spec": """
        Healthcare Management Platform:
        
        1. Patient Portal: Vue.js web application for patient access
        2. Provider Dashboard: React application for healthcare providers
        3. Patient Management: Java Spring Boot service for patient records and demographics
        4. Appointment Service: Python FastAPI service for scheduling and management
        5. Telemedicine Engine: Go service for video consultations and remote care
        6. Medical Records: .NET Core service for EHR management and interoperability
        7. Billing Service: Java service for insurance claims and payment processing
        8. Analytics Engine: Python service for population health and clinical analytics
        9. Data Lake: Apache Hadoop for unstructured medical data
        10. External Systems: HL7 FHIR APIs, insurance providers, pharmacy systems
        """
    },
    {
        "title": "IoT Platform",
        "description": "Internet of Things platform with edge computing",
        "spec": """
        IoT Platform Architecture:
        
        1. Device Gateway: Node.js service for device connectivity and protocol translation
        2. Edge Computing: Python service for local data processing and analytics
        3. Device Management: Java Spring Boot service for device registration and monitoring
        4. Data Ingestion: Go service for high-throughput data collection
        5. Analytics Engine: Python service for real-time and batch analytics
        6. Alert Service: .NET Core service for monitoring and notifications
        7. Device Registry: MongoDB for device metadata and configuration
        8. Time Series Database: InfluxDB for sensor data storage
        9. Message Broker: Apache Kafka for device-to-cloud communication
        10. External Systems: Weather APIs, mapping services, third-party IoT platforms
        """
    }
]

# C4 Generation Configuration
C4_GENERATION_SETTINGS = {
    "enable_system_context": True,
    "enable_container": True,
    "enable_component": True,
    "enable_unified": True,
    "auto_generate": True,
    "save_intermediate": False
}

# Chat Configuration
CHAT_SETTINGS = {
    "max_messages": 100,
    "message_retention_days": 7,
    "enable_export": True,
    "enable_clear": True,
    "auto_scroll": True
}

# Error Handling Configuration
ERROR_HANDLING = {
    "max_retries": 3,
    "retry_delay": 1.0,
    "fallback_to_manual": True,
    "log_errors": True
}

# Performance Configuration
PERFORMANCE = {
    "enable_caching": True,
    "cache_ttl": 3600,  # 1 hour
    "max_concurrent_requests": 5,
    "request_timeout": 30.0
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary"""
    return {
        "openai": {
            "model": OPENAI_MODEL,
            "temperature": OPENAI_TEMPERATURE,
            "max_tokens": OPENAI_MAX_TOKENS
        },
        "content_filtering": {
            "filter_prompt": CONTENT_FILTER_PROMPT,
            "extraction_prompt": TECH_SPEC_EXTRACTION_PROMPT,
            "summarization_prompt": CONTEXT_SUMMARIZATION_PROMPT
        },
        "app": {
            "title": APP_TITLE,
            "icon": APP_ICON,
            "max_context_length": MAX_CONTEXT_LENGTH,
            "auto_generate_threshold": AUTO_GENERATE_THRESHOLD
        },
        "ui": {
            "default_output_dir": DEFAULT_OUTPUT_DIR,
            "sidebar_expanded": SIDEBAR_EXPANDED,
            "layout_wide": LAYOUT_WIDE
        },
        "examples": EXAMPLE_SPECIFICATIONS,
        "c4_generation": C4_GENERATION_SETTINGS,
        "chat": CHAT_SETTINGS,
        "error_handling": ERROR_HANDLING,
        "performance": PERFORMANCE
    }

def validate_config() -> bool:
    """Validate configuration settings"""
    try:
        config = get_config()
        
        # Validate OpenAI settings
        if config["openai"]["temperature"] < 0 or config["openai"]["temperature"] > 2:
            print("❌ Invalid OpenAI temperature setting")
            return False
        
        if config["openai"]["max_tokens"] < 1:
            print("❌ Invalid OpenAI max_tokens setting")
            return False
        
        # Validate app settings
        if config["app"]["max_context_length"] < 1000:
            print("❌ Context length too small")
            return False
        
        if config["app"]["auto_generate_threshold"] < 10:
            print("❌ Auto-generate threshold too small")
            return False
        
        print("✅ Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

if __name__ == "__main__":
    # Print current configuration
    print("🔧 C4 Chatbot Configuration")
    print("=" * 40)
    
    config = get_config()
    for section, settings in config.items():
        print(f"\n📋 {section.upper()}:")
        if isinstance(settings, dict):
            for key, value in settings.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"   {key}: {value[:100]}...")
                else:
                    print(f"   {key}: {value}")
        else:
            print(f"   {settings}")
    
    print("\n" + "=" * 40)
    
    # Validate configuration
    if validate_config():
        print("🎉 Configuration is valid and ready to use!")
    else:
        print("❌ Configuration has issues that need to be fixed")
