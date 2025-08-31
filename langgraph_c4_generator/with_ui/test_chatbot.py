#!/usr/bin/env python3
"""
Test script for the C4 Architecture Generator Chatbot

This script tests the core functionality of the chatbot components.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestChatbotFunctionality(unittest.TestCase):
    """Test cases for chatbot functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
    
    def test_content_filtering_simulation(self):
        """Test content filtering logic"""
        from c4_chatbot_ui import filter_relevant_content
        
        # Test with relevant content
        relevant_text = "I need a web application with React frontend and Node.js backend"
        
        with patch('c4_chatbot_ui.ChatOpenAI') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.invoke.return_value.content = relevant_text
            mock_llm.return_value = mock_instance
            
            result = filter_relevant_content(relevant_text)
            self.assertNotEqual(result, "NO_RELEVANT_CONTENT")
    
    def test_technical_spec_extraction(self):
        """Test technical specification extraction"""
        from c4_chatbot_ui import extract_technical_spec
        
        input_text = "The system should use PostgreSQL and Redis"
        
        with patch('c4_chatbot_ui.ChatOpenAI') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.invoke.return_value.content = "PostgreSQL database and Redis caching"
            mock_llm.return_value = mock_instance
            
            result = extract_technical_spec(input_text)
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
    
    def test_context_update(self):
        """Test context updating functionality"""
        from c4_chatbot_ui import update_spec_context
        
        # Test initial context
        new_input = "React frontend application"
        result = update_spec_context(new_input)
        self.assertEqual(result, new_input)
        
        # Test context combination
        existing_context = "Web application"
        with patch('c4_chatbot_ui.st.session_state') as mock_session:
            mock_session.spec_context = existing_context
            
            result = update_spec_context(new_input)
            self.assertIn(existing_context, result)
            self.assertIn(new_input, result)
    
    def test_session_state_initialization(self):
        """Test session state initialization"""
        from c4_chatbot_ui import init_session_state
        
        # Mock streamlit session state
        mock_session = MagicMock()
        with patch('c4_chatbot_ui.st.session_state', mock_session):
            init_session_state()
            
            # Check that session state variables are accessed
            mock_session.__getitem__.assert_called()
    
    def test_sidebar_rendering(self):
        """Test sidebar rendering functionality"""
        from c4_chatbot_ui import render_sidebar
        
        # Mock streamlit sidebar
        mock_sidebar = MagicMock()
        with patch('c4_chatbot_ui.st.sidebar', mock_sidebar):
            render_sidebar()
            
            # Check that sidebar methods are called
            mock_sidebar.header.assert_called()
    
    def test_chat_interface_rendering(self):
        """Test chat interface rendering"""
        from c4_chatbot_ui import render_chat_interface
        
        # Mock streamlit components
        mock_st = MagicMock()
        with patch('c4_chatbot_ui.st', mock_st):
            render_chat_interface()
            
            # Check that chat components are rendered
            mock_st.subheader.assert_called()
    
    def test_spec_context_rendering(self):
        """Test specification context rendering"""
        from c4_chatbot_ui import render_spec_context
        
        # Mock streamlit components
        mock_st = MagicMock()
        with patch('c4_chatbot_ui.st', mock_st):
            render_spec_context()
            
            # Check that spec context components are rendered
            mock_st.subheader.assert_called()
    
    def test_c4_results_rendering(self):
        """Test C4 results rendering"""
        from c4_chatbot_ui import render_c4_results
        
        # Mock streamlit components
        mock_st = MagicMock()
        with patch('c4_chatbot_ui.st', mock_st):
            render_c4_results()
            
            # Check that C4 results components are rendered
            mock_st.subheader.assert_called()
    
    def test_examples_rendering(self):
        """Test examples rendering"""
        from c4_chatbot_ui import render_examples
        
        # Mock streamlit components
        mock_st = MagicMock()
        with patch('c4_chatbot_ui.st', mock_st):
            render_examples()
            
            # Check that examples are rendered
            mock_st.subheader.assert_called()
    
    def test_main_function(self):
        """Test main function execution"""
        from c4_chatbot_ui import main
        
        # Mock streamlit components
        mock_st = MagicMock()
        with patch('c4_chatbot_ui.st', mock_st):
            # Mock session state initialization
            with patch('c4_chatbot_ui.init_session_state'):
                # Mock rendering functions
                with patch('c4_chatbot_ui.render_sidebar'), \
                     patch('c4_chatbot_ui.render_chat_interface'), \
                     patch('c4_chatbot_ui.render_spec_context'), \
                     patch('c4_chatbot_ui.render_c4_results'), \
                     patch('c4_chatbot_ui.render_examples'):
                    
                    main()
                    
                    # Check that main components are called
                    mock_st.set_page_config.assert_called()
                    mock_st.title.assert_called()

class TestChatbotIntegration(unittest.TestCase):
    """Test cases for chatbot integration"""
    
    def test_imports(self):
        """Test that all required modules can be imported"""
        try:
            import streamlit
            import langchain_openai
            import langchain_core
            import openai
            import dotenv
            print("✅ All required modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import required module: {e}")
    
    def test_environment_setup(self):
        """Test environment setup"""
        # Check if .env file exists or OPENAI_API_KEY is set
        env_file_exists = os.path.exists('.env')
        api_key_set = bool(os.getenv('OPENAI_API_KEY'))
        
        if not env_file_exists and not api_key_set:
            print("⚠️  Warning: No .env file found and OPENAI_API_KEY not set")
            print("   This may cause some functionality to fail")
        else:
            print("✅ Environment properly configured")

def run_tests():
    """Run all tests"""
    print("🧪 Running C4 Chatbot Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestChatbotFunctionality))
    suite.addTests(loader.loadTestsFromTestCase(TestChatbotIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All tests passed!")
    else:
        print(f"❌ {len(result.failures)} tests failed")
        print(f"❌ {len(result.errors)} tests had errors")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
