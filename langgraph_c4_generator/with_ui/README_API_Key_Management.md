# API Key Management System

## Overview

The C4 Architecture Generator Chatbot now includes a **centralized API key management system** that provides a unified way to handle OpenAI API keys across the entire application. This system eliminates the need for repetitive API key extraction code and provides consistent error handling, validation, and user feedback.

## 🆕 New Features

### **1. Centralized API Key Management**
- **Single Source of Truth**: All API key operations go through one manager
- **Multiple Source Support**: Environment variables, .env files, Streamlit secrets
- **Automatic Fallback**: Tries multiple sources in order of priority
- **Caching**: API key is cached for performance

### **2. Enhanced Validation & Security**
- **Format Validation**: Checks OpenAI API key format (starts with "sk-")
- **Length Validation**: Ensures minimum key length requirements
- **Source Tracking**: Tracks where the API key was loaded from
- **Error Handling**: Comprehensive error messages and setup instructions

### **3. User Experience Improvements**
- **Status Display**: Clear visual indicators of API key status
- **Setup Instructions**: Step-by-step guidance for users
- **Health Monitoring**: Real-time API key health status
- **Refresh Capability**: Ability to refresh API key during runtime

## 🏗️ Architecture

### **APIKeyManager Class**
```python
class APIKeyManager:
    def __init__(self):
        self._api_key = None          # Cached API key
        self._key_sources = []        # Sources where key was found
    
    def get_api_key(self) -> Optional[str]
    def is_api_key_available(self) -> bool
    def get_api_key_status(self) -> Dict[str, Any]
    def get_chat_openai_instance(self, model: str, temperature: float) -> ChatOpenAI
    def refresh_api_key(self)
    def get_api_key_display_info(self) -> str
    def get_setup_instructions(self) -> str
```

### **Global Instance**
```python
# Global API key manager instance
api_key_manager = APIKeyManager()
```

## 🔧 Key Methods

### **Core API Key Operations**
- **`get_api_key()`**: Returns the current API key
- **`is_api_key_available()`**: Checks if API key is present
- **`get_api_key_status()`**: Returns comprehensive status information
- **`refresh_api_key()`**: Reloads API key from sources

### **ChatOpenAI Integration**
- **`get_chat_openai_instance()`**: Creates configured ChatOpenAI instances
- **Automatic API Key Injection**: No need to manually pass API keys
- **Error Handling**: Clear error messages when API key is missing

### **User Interface Support**
- **`get_api_key_display_info()`**: User-friendly status messages
- **`get_setup_instructions()`**: Comprehensive setup guidance
- **Status Validation**: Real-time validation and health checks

## 📊 API Key Sources

### **Priority Order**
1. **Streamlit Secrets** (for Streamlit Cloud deployment)
2. **Environment Variables** (system environment)
3. **Direct Environment Access** (fallback)
4. **.env File** (with override)

### **Source Detection**
```python
# Example status output
{
    "available": True,
    "sources": ["Environment Variable"],
    "key_length": 51,
    "key_prefix": "sk-1234...",
    "validation": {"valid": True, "error": None}
}
```

## 🎯 Usage Examples

### **Basic API Key Check**
```python
from c4_chatbot_ui import api_key_manager

# Check if API key is available
if api_key_manager.is_api_key_available():
    print("✅ API key is available")
else:
    print("❌ API key is missing")
```

### **Create ChatOpenAI Instance**
```python
# Create LLM instance with managed API key
try:
    llm = api_key_manager.get_chat_openai_instance(
        model="gpt-4", 
        temperature=0.1
    )
    response = llm.invoke("Hello, world!")
except ValueError as e:
    print(f"API key error: {e}")
```

### **Get Status Information**
```python
# Get comprehensive status
status = api_key_manager.get_api_key_status()
print(f"Available: {status['available']}")
print(f"Sources: {status['sources']}")
print(f"Valid: {status['validation']['valid']}")
```

## 🚀 Utility Functions

### **Availability Checking**
```python
from c4_chatbot_ui import check_api_key_availability

# Check API key availability
if check_api_key_availability():
    # Proceed with AI operations
    pass
else:
    # Handle missing API key
    pass
```

### **Error Messages**
```python
from c4_chatbot_ui import get_api_key_error_message

# Get user-friendly error message
error_msg = get_api_key_error_message()
print(error_msg)
```

### **Decorator Support**
```python
from c4_chatbot_ui import require_api_key

@require_api_key
def ai_operation():
    # This function will only run if API key is available
    pass
```

## 📱 User Interface Integration

### **Sidebar Status Display**
- **Success Indicator**: ✅ when API key is valid
- **Warning Indicator**: ⚠️ when API key has issues
- **Error Indicator**: ❌ when API key is missing
- **Source Information**: Shows where API key was loaded from

### **Main Interface Status**
- **API Key Status Section**: Comprehensive status information
- **Health Check**: Real-time health monitoring
- **Setup Instructions**: Expandable setup guidance
- **Quick Actions**: Refresh and status check buttons

### **Enhanced Error Handling**
- **Clear Error Messages**: User-friendly error descriptions
- **Setup Instructions**: Step-by-step resolution guidance
- **Status Monitoring**: Real-time status updates

## 🔒 Security Features

### **API Key Validation**
- **Format Checking**: Ensures OpenAI API key format
- **Length Validation**: Minimum length requirements
- **Source Tracking**: Audit trail of key sources
- **No Hardcoding**: Keys are never stored in code

### **Environment Isolation**
- **Source Priority**: Secure source selection
- **Fallback Handling**: Graceful degradation
- **Error Isolation**: Failures don't crash the application

## 🧪 Testing

### **Run API Key Tests**
```bash
cd with_ui
python test_api_key_manager.py
```

### **Test Scenarios**
1. **No API Key**: Test behavior when no key is set
2. **Invalid Format**: Test with malformed keys
3. **Valid Keys**: Test with properly formatted keys
4. **Source Switching**: Test different key sources
5. **Refresh Functionality**: Test key refresh capability

### **Integration Testing**
```bash
# Test with real API key
export OPENAI_API_KEY='your-actual-key-here'
python test_api_key_manager.py

# Test in Streamlit
streamlit run c4_chatbot_ui.py
```

## 📋 Setup Instructions

### **Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### **Create .env File**
```bash
# Create .env file in project directory
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### **Streamlit Secrets (Cloud Deployment)**
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-api-key-here"
```

## 🔄 Migration Guide

### **Before (Old Way)**
```python
# Scattered throughout the code
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not set")

llm = ChatOpenAI(
    model="gpt-4",
    api_key=api_key,
    temperature=0.1
)
```

### **After (New Way)**
```python
# Centralized and consistent
from c4_chatbot_ui import api_key_manager

llm = api_key_manager.get_chat_openai_instance(
    model="gpt-4",
    temperature=0.1
)
```

## 🚧 Error Handling

### **Common Error Scenarios**
1. **No API Key**: Clear setup instructions provided
2. **Invalid Format**: Specific format requirements shown
3. **Source Issues**: Multiple source options presented
4. **Network Issues**: Graceful fallback handling

### **Error Recovery**
- **Automatic Refresh**: Try to reload API key
- **Source Fallback**: Try alternative sources
- **User Guidance**: Clear resolution steps
- **Status Monitoring**: Real-time error detection

## 📚 Related Documentation

- [README_Comprehensive.md](README_Comprehensive.md) - Complete chatbot documentation
- [README_Tab_Features.md](README_Tab_Features.md) - Tab functionality guide
- [README_Persona_Features.md](README_Persona_Features.md) - Persona features guide
- [c4_chatbot_ui.py](c4_chatbot_ui.py) - Main chatbot implementation
- [test_api_key_manager.py](test_api_key_manager.py) - API key management tests

## 🤝 Contributing

To contribute to API key management:
1. **Enhance Validation**: Add more sophisticated key validation
2. **Add Sources**: Support additional key source types
3. **Improve Security**: Add encryption or additional security measures
4. **UI Enhancements**: Better status display and user feedback

## 📞 Support

For questions about API key management:
- Check the test script for usage examples
- Review the APIKeyManager class implementation
- Examine the utility functions
- Run the test suite to verify functionality

---

**Note**: The new API key management system maintains full backward compatibility while providing significant improvements in security, user experience, and code maintainability. All existing functionality continues to work, now with better error handling and user guidance! 🔑✨
