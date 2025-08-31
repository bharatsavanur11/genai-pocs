#!/usr/bin/env python3
"""
Test script for the C4 Chatbot Conversation Memory System

This script tests the core memory functionality to ensure it works correctly.
"""

import unittest
import os
import tempfile
import pickle
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestConversationMemory(unittest.TestCase):
    """Test cases for ConversationMemory class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.memory_file = os.path.join(self.test_dir, "test_memory.pkl")
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        
        # Remove test files
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_memory_initialization(self):
        """Test memory initialization"""
        from c4_chatbot_ui import ConversationMemory
        
        memory = ConversationMemory(self.memory_file)
        
        # Check default structure
        self.assertIn('conversations', memory.memory)
        self.assertIn('global_context', memory.memory)
        self.assertIn('last_updated', memory.memory)
        self.assertIn('session_count', memory.memory)
        
        # Check default values
        self.assertEqual(len(memory.memory['conversations']), 0)
        self.assertEqual(memory.memory['global_context'], "")
    
    def test_add_conversation(self):
        """Test adding conversations to memory"""
        from c4_chatbot_ui import ConversationMemory
        
        memory = ConversationMemory(self.memory_file)
        
        # Add a conversation
        conversation_id = "test_session_1"
        spec_context = "React frontend with Node.js backend"
        messages = [{"role": "user", "content": "Test message"}]
        
        memory.add_conversation(conversation_id, spec_context, messages)
        
        # Check conversation was added
        self.assertEqual(len(memory.memory['conversations']), 1)
        self.assertEqual(memory.memory['conversations'][0]['id'], conversation_id)
        self.assertEqual(memory.memory['conversations'][0]['spec_context'], spec_context)
        self.assertEqual(memory.memory['conversations'][0]['message_count'], 1)
    
    def test_memory_persistence(self):
        """Test memory persistence to file"""
        from c4_chatbot_ui import ConversationMemory
        
        memory = ConversationMemory(self.memory_file)
        
        # Add a conversation
        memory.add_conversation("test_session", "Test context", [])
        
        # Check file was created
        self.assertTrue(os.path.exists(self.memory_file))
        
        # Load memory from file
        new_memory = ConversationMemory(self.memory_file)
        
        # Check data was preserved
        self.assertEqual(len(new_memory.memory['conversations']), 1)
        self.assertEqual(new_memory.memory['conversations'][0]['spec_context'], "Test context")
    
    def test_content_hashing(self):
        """Test content hashing functionality"""
        from c4_chatbot_ui import ConversationMemory
        
        memory = ConversationMemory(self.memory_file)
        
        # Test hash generation
        content1 = "React frontend application"
        content2 = "React frontend application"  # Same content
        content3 = "Node.js backend service"     # Different content
        
        hash1 = memory._hash_content(content1)
        hash2 = memory._hash_content(content2)
        hash3 = memory._hash_content(content3)
        
        # Same content should have same hash
        self.assertEqual(hash1, hash2)
        
        # Different content should have different hashes
        self.assertNotEqual(hash1, hash3)
        
        # Hash should be consistent
        self.assertEqual(hash1, memory._hash_content(content1))
    
    def test_similarity_calculation(self):
        """Test similarity calculation between texts"""
        from c4_chatbot_ui import ConversationMemory
        
        memory = ConversationMemory(self.memory_file)
        
        # Test similar texts
        text1 = "React frontend application"
        text2 = "React frontend with TypeScript"
        text3 = "Node.js backend service"
        
        similarity_high = memory._calculate_similarity(text1, text2)
        similarity_low = memory._calculate_similarity(text1, text3)
        
        # Similar texts should have higher similarity
        self.assertGreater(similarity_high, similarity_low)
        
        # Similarity should be between 0 and 1
        self.assertGreaterEqual(similarity_high, 0.0)
        self.assertLessEqual(similarity_high, 1.0)
        
        # Same text should have similarity 1.0
        self.assertEqual(memory._calculate_similarity(text1, text1), 1.0)
    
    def test_relevant_context_retrieval(self):
        """Test relevant context retrieval"""
        from c4_chatbot_ui import ConversationMemory
        
        memory = ConversationMemory(self.memory_file)
        
        # Add some test conversations
        conversations = [
            ("session1", "React frontend application", []),
            ("session2", "Node.js backend service", []),
            ("session3", "PostgreSQL database design", []),
            ("session4", "React component architecture", [])
        ]
        
        for conv_id, spec_context, messages in conversations:
            memory.add_conversation(conv_id, spec_context, messages)
        
        # Search for relevant contexts
        current_context = "React frontend with components"
        relevant = memory.get_relevant_context(current_context, max_results=3)
        
        # Should find relevant contexts
        self.assertGreater(len(relevant), 0)
        
        # React-related contexts should have higher similarity
        react_contexts = [ctx for ctx in relevant if 'React' in ctx['spec_context']]
        if react_contexts:
            self.assertGreater(react_contexts[0]['similarity'], 0.1)
    
    def test_global_context_update(self):
        """Test global context updating"""
        from c4_chatbot_ui import ConversationMemory
        
        memory = ConversationMemory(self.memory_file)
        
        # Add conversations to build global context
        memory.add_conversation("session1", "React frontend", [])
        memory.add_conversation("session2", "Node.js backend", [])
        
        # Check global context was updated
        global_context = memory.get_global_context()
        self.assertIn("React", global_context)
        self.assertIn("Node.js", global_context)
    
    def test_memory_limits(self):
        """Test memory size limits"""
        from c4_chatbot_ui import ConversationMemory, MAX_CONVERSATIONS
        
        memory = ConversationMemory(self.memory_file)
        
        # Add more conversations than the limit
        for i in range(MAX_CONVERSATIONS + 5):
            memory.add_conversation(f"session_{i}", f"Context {i}", [])
        
        # Should maintain only the most recent conversations
        self.assertEqual(len(memory.memory['conversations']), MAX_CONVERSATIONS)
        
        # Most recent should be preserved
        recent_ids = [conv['id'] for conv in memory.memory['conversations']]
        self.assertIn(f"session_{MAX_CONVERSATIONS + 4}", recent_ids)
        self.assertNotIn("session_0", recent_ids)

class TestContextManager(unittest.TestCase):
    """Test cases for ContextManager class"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock conversation memory
        self.mock_memory = MagicMock()
        self.mock_memory.get_relevant_context.return_value = []
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
    
    def test_context_manager_initialization(self):
        """Test context manager initialization"""
        from c4_chatbot_ui import ContextManager
        
        context_manager = ContextManager(self.mock_memory)
        
        # Check session ID was generated
        self.assertIsNotNone(context_manager.current_session_id)
        self.assertTrue(context_manager.current_session_id.startswith("session_"))
    
    def test_context_merging(self):
        """Test context merging functionality"""
        from c4_chatbot_ui import ContextManager
        
        context_manager = ContextManager(self.mock_memory)
        
        # Test merging contexts
        current_context = "React frontend"
        new_input = "Node.js backend"
        
        merged_context, relevant_contexts = context_manager.merge_contexts(
            current_context, new_input, use_global_context=False
        )
        
        # Should combine contexts
        self.assertIn("React", merged_context)
        self.assertIn("Node.js", merged_context)
        self.assertIn("Additional Context", merged_context)
    
    def test_conversation_summary_creation(self):
        """Test conversation summary creation"""
        from c4_chatbot_ui import ContextManager
        
        context_manager = ContextManager(self.mock_memory)
        
        # Create summary
        spec_context = "Test specification"
        messages = [{"role": "user", "content": "Test"}]
        result = {"success": True, "systems": [{"name": "Test System"}]}
        
        summary = context_manager.create_conversation_summary(
            spec_context, messages, result
        )
        
        # Check summary structure
        self.assertIn('session_id', summary)
        self.assertIn('timestamp', summary)
        self.assertIn('spec_context', summary)
        self.assertIn('message_count', summary)
        self.assertIn('result_summary', summary)
        self.assertIn('context_length', summary)

def run_memory_tests():
    """Run all memory system tests"""
    print("🧪 Running C4 Chatbot Memory System Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConversationMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestContextManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 All memory system tests passed!")
    else:
        print(f"❌ {len(result.failures)} tests failed")
        print(f"❌ {len(result.errors)} tests had errors")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_memory_tests()
    sys.exit(0 if success else 1)
