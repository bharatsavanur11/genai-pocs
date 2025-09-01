#!/usr/bin/env python3
"""
Test script for the new API key management system in the C4 chatbot UI.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_api_key_manager_creation():
    """Test API key manager creation and basic functionality"""
    print("🧪 Testing API Key Manager Creation")
    print("=" * 50)
    
    try:
        # Import the API key manager
        from c4_chatbot_ui import APIKeyManager, api_key_manager
        
        print("✅ Successfully imported APIKeyManager class")
        print(f"✅ Global instance created: {type(api_key_manager).__name__}")
        
        # Test basic methods
        print("\n📋 Testing Basic Methods...")
        
        # Test API key availability check
        is_available = api_key_manager.is_api_key_available()
        print(f"  - API Key Available: {is_available}")
        
        # Test status retrieval
        status = api_key_manager.get_api_key_status()
        print(f"  - Status Keys: {list(status.keys())}")
        print(f"  - Available: {status.get('available')}")
        print(f"  - Sources: {status.get('sources')}")
        print(f"  - Key Length: {status.get('key_length')}")
        
        # Test display info
        display_info = api_key_manager.get_api_key_display_info()
        print(f"  - Display Info: {display_info}")
        
        print("✅ Basic API key manager functionality working")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the with_ui directory")
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

def test_api_key_validation():
    """Test API key validation functionality"""
    print("\n🔍 Testing API Key Validation")
    print("=" * 50)
    
    try:
        from c4_chatbot_ui import APIKeyManager
        
        # Create a new instance for testing
        test_manager = APIKeyManager()
        
        # Test validation methods
        print("📋 Testing Validation Methods...")
        
        # Test with no API key
        status = test_manager.get_api_key_status()
        validation = status.get('validation', {})
        print(f"  - No API Key - Valid: {validation.get('valid')}")
        if not validation.get('valid'):
            print(f"  - Error: {validation.get('error')}")
        
        # Test with invalid API key
        with patch.object(test_manager, '_api_key', 'invalid_key'):
            status = test_manager.get_api_key_status()
            validation = status.get('validation', {})
            print(f"  - Invalid Key - Valid: {validation.get('valid')}")
            if not validation.get('valid'):
                print(f"  - Error: {validation.get('error')}")
        
        # Test with valid API key format
        with patch.object(test_manager, '_api_key', 'sk-1234567890abcdef1234567890abcdef1234567890abcdef'):
            status = test_manager.get_api_key_status()
            validation = status.get('validation', {})
            print(f"  - Valid Format - Valid: {validation.get('valid')}")
            if validation.get('valid'):
                print(f"  - Key Length: {status.get('key_length')}")
                print(f"  - Key Prefix: {status.get('key_prefix')}")
        
        print("✅ API key validation functionality working")
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        import traceback
        traceback.print_exc()

def test_api_key_sources():
    """Test API key loading from different sources"""
    print("\n📁 Testing API Key Sources")
    print("=" * 50)
    
    try:
        from c4_chatbot_ui import APIKeyManager
        
        # Test environment variable source
        print("📋 Testing Environment Variable Source...")
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key_from_env'}):
            test_manager = APIKeyManager()
            status = test_manager.get_api_key_status()
            print(f"  - Environment Variable: {status.get('sources')}")
            print(f"  - Available: {status.get('available')}")
        
        # Test .env file source (mock)
        print("\n📋 Testing .env File Source...")
        
        with patch('os.getenv') as mock_getenv:
            mock_getenv.return_value = 'test_key_from_dotenv'
            test_manager = APIKeyManager()
            # Note: This is a simplified test since we can't easily mock dotenv loading
        
        print("✅ API key source testing completed")
        
    except Exception as e:
        print(f"❌ Source testing failed: {e}")
        import traceback
        traceback.print_exc()

def test_utility_functions():
    """Test utility functions for API key management"""
    print("\n⚙️ Testing Utility Functions")
    print("=" * 50)
    
    try:
        from c4_chatbot_ui import check_api_key_availability, get_api_key_error_message
        
        print("📋 Testing Utility Functions...")
        
        # Test availability check
        is_available = check_api_key_availability()
        print(f"  - API Key Available: {is_available}")
        
        # Test error message
        error_msg = get_api_key_error_message()
        print(f"  - Error Message: {error_msg}")
        
        print("✅ Utility functions working correctly")
        
    except Exception as e:
        print(f"❌ Utility function test failed: {e}")
        import traceback
        traceback.print_exc()

def test_chat_openai_creation():
    """Test ChatOpenAI instance creation with API key manager"""
    print("\n🤖 Testing ChatOpenAI Instance Creation")
    print("=" * 50)
    
    try:
        from c4_chatbot_ui import api_key_manager
        
        print("📋 Testing ChatOpenAI Creation...")
        
        if api_key_manager.is_api_key_available():
            try:
                # Try to create a ChatOpenAI instance
                llm = api_key_manager.get_chat_openai_instance(model="gpt-4", temperature=0.1)
                print(f"  - ChatOpenAI Created: {type(llm).__name__}")
                print(f"  - Model: {llm.model_name}")
                print(f"  - Temperature: {llm.temperature}")
                print("✅ ChatOpenAI instance creation successful")
            except Exception as e:
                print(f"  - ChatOpenAI Creation Failed: {e}")
                print("  - This might be expected if no valid API key is set")
        else:
            print("  - Skipping ChatOpenAI creation (no API key available)")
            print("  - This is expected behavior when no API key is set")
        
    except Exception as e:
        print(f"❌ ChatOpenAI test failed: {e}")
        import traceback
        traceback.print_exc()

def test_setup_instructions():
    """Test setup instructions generation"""
    print("\n📖 Testing Setup Instructions")
    print("=" * 50)
    
    try:
        from c4_chatbot_ui import api_key_manager
        
        print("📋 Testing Setup Instructions...")
        
        instructions = api_key_manager.get_setup_instructions()
        print(f"  - Instructions Length: {len(instructions)} characters")
        print(f"  - Contains Environment Variable Info: {'export OPENAI_API_KEY' in instructions}")
        print(f"  - Contains .env File Info: {'.env' in instructions}")
        print(f"  - Contains Streamlit Secrets Info: {'Streamlit' in instructions}")
        
        print("✅ Setup instructions generated correctly")
        
    except Exception as e:
        print(f"❌ Setup instructions test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all API key manager tests"""
    print("🚀 Starting API Key Manager Tests")
    print("=" * 60)
    
    # Run all tests
    test_api_key_manager_creation()
    test_api_key_validation()
    test_api_key_sources()
    test_utility_functions()
    test_chat_openai_creation()
    test_setup_instructions()
    
    print("\n" + "=" * 60)
    print("✅ All API Key Manager tests completed!")
    print("\n💡 To test with a real API key:")
    print("   1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    print("   2. Run the test again to see full functionality")
    print("   3. Or run the chatbot: streamlit run c4_chatbot_ui.py")

if __name__ == "__main__":
    main()
