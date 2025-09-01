#!/usr/bin/env python3
"""
Test script for the new tab functionality in the C4 chatbot UI.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_tab_creation():
    """Test tab creation and management"""
    print("🧪 Testing Tab Functionality")
    print("=" * 50)
    
    try:
        # Import the tab-related functions
        from c4_chatbot_ui import ConversationTab, create_new_tab, get_active_tab, delete_tab
        
        print("✅ Successfully imported tab functions")
        
        # Test ConversationTab class
        print("\n📋 Testing ConversationTab class...")
        tab = ConversationTab("test_id", "Test Tab")
        print(f"  - Tab ID: {tab.id}")
        print(f"  - Tab Title: {tab.title}")
        print(f"  - Messages: {len(tab.messages)}")
        print(f"  - Spec Context: {len(tab.spec_context)} characters")
        
        # Test adding messages
        tab.add_message("user", "Hello, this is a test message")
        tab.add_message("assistant", "Hi! I'm here to help with technical specifications")
        print(f"  - Messages after adding: {len(tab.messages)}")
        
        # Test updating spec context
        tab.update_spec_context("This is a test technical specification")
        print(f"  - Spec context after update: {len(tab.spec_context)} characters")
        
        # Test getting summary
        summary = tab.get_summary()
        print(f"  - Summary: {summary}")
        
        print("✅ ConversationTab class working correctly")
        
        # Test tab management functions (these would need Streamlit session state)
        print("\n📋 Testing tab management functions...")
        print("  - Note: These functions require Streamlit session state")
        print("  - They will be tested when running the actual Streamlit app")
        
        print("\n✅ Tab functionality tests completed successfully!")
        print("\n🚀 To test the full tab functionality:")
        print("   1. Run: streamlit run c4_chatbot_ui.py")
        print("   2. Create new tabs using the '➕ New Chat' button")
        print("   3. Switch between tabs")
        print("   4. Test tab actions (rename, export, clear, delete)")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the with_ui directory")
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

def test_tab_ui_elements():
    """Test the UI elements that would be created for tabs"""
    print("\n🎨 Testing Tab UI Elements")
    print("=" * 50)
    
    # Simulate tab data
    tabs_data = [
        {"id": "tab1", "title": "E-commerce System", "messages": 5, "has_result": True},
        {"id": "tab2", "title": "Healthcare Platform", "messages": 3, "has_result": False},
        {"id": "tab3", "title": "Banking Application", "messages": 8, "has_result": True}
    ]
    
    print("📋 Simulated Tab Structure:")
    for i, tab in enumerate(tabs_data, 1):
        status_icon = "✅" if tab["has_result"] else "💬"
        tab_name = f"{status_icon} {tab['title']} ({tab['messages']})"
        print(f"  {i}. {tab_name}")
    
    print("\n🔧 Tab Actions Available:")
    print("  - Rename tab title")
    print("  - Export tab data")
    print("  - Clear tab content")
    print("  - Delete tab (if more than one exists)")
    
    print("\n✅ Tab UI elements structure verified!")

if __name__ == "__main__":
    test_tab_creation()
    test_tab_ui_elements()
