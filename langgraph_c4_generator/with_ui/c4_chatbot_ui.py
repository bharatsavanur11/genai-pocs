#!/usr/bin/env python3
"""
C4 Architecture Generator Chatbot UI

A Streamlit-based chatbot interface that:
1. Takes technical specification as input in text box
2. Understands the text and maintains conversation context
3. Generates C4 Diagrams based on text
4. Considers older relevant inputs as entire context when user adds additional context
5. Ignores the content that is not relevant to technical specification
6. Remembers previous conversations across sessions
7. Intelligently appends earlier contexts

Features:
- Chat-like interface with message history
- Context-aware specification building
- Real-time C4 diagram generation
- Smart content filtering
- Multiple diagram level views
- Persistent conversation memory
- Session persistence
- Intelligent context merging
"""

import json
import os
import re
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import uuid

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Import the C4 generator
from c4_generator_new import generate_c4_architecture, save_dsl_files

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Constants
APP_TITLE = "C4 Architecture Generator Chatbot"
MAX_CONTEXT_LENGTH = 8000  # Maximum context length to prevent token overflow
MEMORY_FILE = "chatbot_memory.pkl"
CONVERSATION_HISTORY_FILE = "conversation_history.json"
MAX_CONVERSATIONS = 50  # Maximum number of conversations to remember

class APIKeyManager:
    """
    Centralized API key management for the C4 chatbot.
    
    This class provides a unified way to:
    - Extract API keys from multiple sources (environment, Streamlit secrets, .env files)
    - Validate API key presence and format
    - Provide consistent error handling and user feedback
    - Cache API key for performance
    
    Attributes:
        _api_key (Optional[str]): Cached API key value
        _key_sources (List[str]): List of sources checked for API key
    """
    
    def __init__(self):
        """Initialize the API key manager."""
        self._api_key = None
        self._key_sources = []
        self._load_api_key()
    
    def _load_api_key(self):
        """
        Load API key from multiple sources in order of priority.
        
        Sources checked (in order):
        1. Streamlit secrets first (for Streamlit Cloud deployment)
        2. Environment variables (.env file or system environment)
        3. Direct environment variable access
        """
        # Try Streamlit secrets first (for Streamlit Cloud)
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                self._api_key = st.secrets["OPENAI_API_KEY"]
                self._key_sources.append("Streamlit Secrets")
                return
        except Exception:
            pass
        
        # Try environment variables
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            self._api_key = env_key
            self._key_sources.append("Environment Variable")
            return
        
        # Try .env file directly
        try:
            from dotenv import load_dotenv
            load_dotenv(override=True)
            env_key = os.getenv("OPENAI_API_KEY")
            if env_key:
                self._api_key = env_key
                self._key_sources.append(".env File")
                return
        except Exception:
            pass
        
        # No API key found
        self._api_key = None
        self._key_sources = []
    
    def get_api_key(self) -> Optional[str]:
        """
        Get the current API key.
        
        Returns:
            Optional[str]: The API key if available, None otherwise
        """
        return self._api_key
    
    def is_api_key_available(self) -> bool:
        """
        Check if an API key is available.
        
        Returns:
            bool: True if API key is available, False otherwise
        """
        return bool(self._api_key)
    
    def get_api_key_status(self) -> Dict[str, Any]:
        """
        Get comprehensive API key status information.
        
        Returns:
            Dict[str, Any]: Status information including availability, sources, and validation
        """
        status = {
            "available": self.is_api_key_available(),
            "sources": self._key_sources.copy(),
            "key_length": len(self._api_key) if self._api_key else 0,
            "key_prefix": self._api_key[:7] + "..." if self._api_key and len(self._api_key) > 7 else None,
            "validation": self._validate_api_key_format()
        }
        return status
    
    def _validate_api_key_format(self) -> Dict[str, Any]:
        """
        Validate the API key format (basic validation).
        
        Returns:
            Dict[str, Any]: Validation results
        """
        if not self._api_key:
            return {"valid": False, "error": "No API key available"}
        
        # Basic OpenAI API key validation
        if not self._api_key.startswith("sk-"):
            return {"valid": False, "error": "Invalid OpenAI API key format (should start with 'sk-')"}
        
        if len(self._api_key) < 20:
            return {"valid": False, "error": "API key too short"}
        
        return {"valid": True, "error": None}
    
    def refresh_api_key(self):
        """
        Refresh the API key from sources.
        
        Useful when the API key might have been updated during runtime.
        """
        self._api_key = None
        self._key_sources = []
        self._load_api_key()
    
    def get_chat_openai_instance(self, model: str = "gpt-4", temperature: float = 0.1) -> ChatOpenAI:
        """
        Create a ChatOpenAI instance with the managed API key.
        
        Args:
            model (str): OpenAI model to use (default: "gpt-4")
            temperature (float): Model temperature (default: 0.1)
            
        Returns:
            ChatOpenAI: Configured ChatOpenAI instance
            
        Raises:
            ValueError: If no API key is available
        """
        if not self.is_api_key_available():
            raise ValueError("OpenAI API key not available. Please set OPENAI_API_KEY in your environment or .env file.")
        
        return ChatOpenAI(
            model=model,
            api_key=self._api_key,
            temperature=temperature
        )
    
    def get_api_key_display_info(self) -> str:
        """
        Get user-friendly API key status information.
        
        Returns:
            str: Formatted status message for display
        """
        if self.is_api_key_available():
            validation = self._validate_api_key_format()
            if validation["valid"]:
                return f"✅ OpenAI API Key Available (from: {', '.join(self._key_sources)})"
            else:
                return f"⚠️ API Key Found but Invalid: {validation['error']}"
        else:
            return "❌ OpenAI API Key Missing"
    
    def get_setup_instructions(self) -> str:
        """
        Get instructions for setting up the API key.
        
        Returns:
            str: Setup instructions for users
        """
        return """
        To set up your OpenAI API key:
        
        1. **Environment Variable (Recommended):**
           ```bash
           export OPENAI_API_KEY='your-api-key-here'
           ```
        
        2. **Create a .env file:**
           Create a file named `.env` in the project directory with:
           ```
           OPENAI_API_KEY=your-api-key-here
           ```
        
        3. **Streamlit Secrets (for Streamlit Cloud):**
           Add to your Streamlit secrets configuration
        
        **Note:** Replace 'your-api-key-here' with your actual OpenAI API key.
        You can get one from: https://platform.openai.com/api-keys
        """

# Global API key manager instance
api_key_manager = APIKeyManager()

def check_api_key_availability() -> bool:
    """
    Check if API key is available for AI operations.
    
    Returns:
        bool: True if API key is available and valid, False otherwise
    """
    return api_key_manager.is_api_key_available() and api_key_manager.get_api_key_status()["validation"]["valid"]

def get_api_key_error_message() -> str:
    """
    Get a user-friendly error message when API key is not available.
    
    Returns:
        str: Error message explaining the issue and how to fix it
    """
    status = api_key_manager.get_api_key_status()
    
    if not status["available"]:
        return "❌ OpenAI API key not found. Please set your API key to use AI features."
    
    if not status["validation"]["valid"]:
        return f"⚠️ API key validation failed: {status['validation']['error']}"
    
    return "✅ API key is available and valid."

def require_api_key(func):
    """
    Decorator to require API key availability for functions.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function that checks API key before execution
    """
    def wrapper(*args, **kwargs):
        if not check_api_key_availability():
            st.error(get_api_key_error_message())
            with st.expander("📋 How to set up your API key"):
                st.markdown(api_key_manager.get_setup_instructions())
            return None
        return func(*args, **kwargs)
    return wrapper

class ConversationMemory:
    """
    Manages persistent conversation memory across sessions.
    
    This class provides a sophisticated memory system that:
    - Stores conversations persistently across browser sessions
    - Maintains a global context from all conversations
    - Provides intelligent context retrieval and similarity scoring
    - Handles memory size limits and summarization
    
    Attributes:
        memory_file (str): Path to the pickle file storing memory data
        memory (Dict): In-memory representation of stored conversations
    """
    
    def __init__(self, memory_file: str = MEMORY_FILE):
        """
        Initialize the conversation memory system.
        
        Args:
            memory_file (str): Path to the memory storage file
        """
        self.memory_file = memory_file
        self.memory = self.load_memory()
    
    def load_memory(self) -> Dict[str, Any]:
        """
        Load conversation memory from persistent storage.
        
        Attempts to load existing memory from pickle file. If loading fails
        or no file exists, returns a default memory structure.
        
        Returns:
            Dict: Memory structure with conversations, global context, and metadata
        """
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"Warning: Could not load memory file: {e}")
        
        return {
            'conversations': [],
            'global_context': "",
            'last_updated': datetime.now().isoformat(),
            'session_count': 0
        }
    
    def save_memory(self):
        """
        Save conversation memory to persistent storage.
        
        Serializes the current memory state to a pickle file and updates
        the last_updated timestamp. Handles errors gracefully with warnings.
        """
        try:
            self.memory['last_updated'] = datetime.now().isoformat()
            with open(self.memory_file, 'wb') as f:
                pickle.dump(self.memory, f)
        except Exception as e:
            print(f"Warning: Could not save memory file: {e}")
    
    def add_conversation(self, conversation_id: str, spec_context: str, 
                        messages: List[Dict], result: Optional[Dict] = None):
        """
        Add a new conversation to the memory system.
        
        Creates a conversation record with metadata, adds it to the conversations
        list, enforces memory limits, and updates the global context.
        
        Args:
            conversation_id (str): Unique identifier for the conversation
            spec_context (str): Technical specification context
            messages (List[Dict]): List of chat messages
            result (Optional[Dict]): C4 generation result if available
        """
        conversation = {
            'id': conversation_id,
            'timestamp': datetime.now().isoformat(),
            'spec_context': spec_context,
            'message_count': len(messages),
            'result_summary': self._summarize_result(result) if result else None,
            'hash': self._hash_content(spec_context)
        }
        
        # Add to conversations list
        self.memory['conversations'].append(conversation)
        
        # Keep only the most recent conversations
        if len(self.memory['conversations']) > MAX_CONVERSATIONS:
            self.memory['conversations'] = self.memory['conversations'][-MAX_CONVERSATIONS:]
        
        # Update global context
        self._update_global_context(spec_context)
        
        self.save_memory()
    
    def _hash_content(self, content: str) -> str:
        """
        Generate MD5 hash for content to detect duplicates.
        
        Args:
            content (str): Content to hash
            
        Returns: 
            str: MD5 hash string for duplicate detection
        """
        return hashlib.md5(content.encode()).hexdigest()
    
    def _summarize_result(self, result: Dict) -> Optional[Dict]:
        """
        Create a summary of C4 generation result for storage.
        
        Extracts key metrics from the C4 generation result to create
        a compact summary suitable for memory storage.
        
        Args:
            result (Dict): C4 generation result dictionary
            
        Returns:
            Optional[Dict]: Summary with counts and flags, or None if no result
        """
        if not result or not result.get('success'):
            return None
        
        return {
            'systems_count': len(result.get('systems', [])),
            'containers_count': len(result.get('containers', [])),
            'components_count': len(result.get('components', [])),
            'relationships_count': len(result.get('relationships', [])),
            'has_dsl': bool(result.get('dsl', {}))
        }
    
    def _update_global_context(self, new_context: str):
        """
        Update global context with new information from conversations.
        
        Combines new context with existing global context. If the combined
        context exceeds the maximum length, uses AI summarization to maintain
        focus while preserving important architectural details.
        
        Args:
            new_context (str): New technical specification context to add
        """
        if not self.memory['global_context']:
            self.memory['global_context'] = new_context
        else:
            # Combine with existing global context
            combined = f"{self.memory['global_context']}\n\nAdditional Global Context:\n{new_context}"
            
            # If too long, summarize
            if len(combined) > MAX_CONTEXT_LENGTH:
                try:
                    llm = api_key_manager.get_chat_openai_instance(model="gpt-4", temperature=0.1)
                    
                    prompt = f"""
                    Summarize the following combined technical specifications while preserving all important architectural details:

                    {combined}

                    Create a concise but comprehensive summary that includes:
                    - All system components
                    - Key relationships
                    - Technology choices
                    - External integrations
                    - Important architectural decisions

                    Keep the summary under {MAX_CONTEXT_LENGTH} characters.
                    """
                    
                    response = llm.invoke(prompt)
                    self.memory['global_context'] = response.content.strip()
                except Exception as e:
                    print(f"Warning: Could not summarize global context: {e}")
                    # Fallback: keep recent content
                    self.memory['global_context'] = combined[-MAX_CONTEXT_LENGTH:]
            else:
                self.memory['global_context'] = combined
    
    def get_relevant_context(self, current_context: str, max_results: int = 5) -> List[Dict]:
        """
        Get relevant previous conversations based on current context.
        
        Analyzes the current technical specification context and finds
        previous conversations that are semantically similar. Uses content
        hashing to avoid exact duplicates and similarity scoring to rank
        relevance.
        
        Args:
            current_context (str): Current technical specification context
            max_results (int): Maximum number of relevant contexts to return
            
        Returns:
            List[Dict]: List of relevant conversations with similarity scores
        """
        if not current_context or not self.memory['conversations']:
            return []
        
        # Calculate relevance scores
        relevant_conversations = []
        current_hash = self._hash_content(current_context)
        
        for conv in self.memory['conversations']:
            if conv['hash'] == current_hash:
                continue  # Skip exact duplicates
            
            # Calculate similarity score (simple keyword matching for now)
            similarity = self._calculate_similarity(current_context, conv['spec_context'])
            
            if similarity > 0.1:  # Minimum similarity threshold
                relevant_conversations.append({
                    **conv,
                    'similarity': similarity
                })
        
        # Sort by similarity and recency
        relevant_conversations.sort(key=lambda x: (x['similarity'], x['timestamp']), reverse=True)
        
        return relevant_conversations[:max_results]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using keyword matching.
        
        Uses Jaccard similarity (intersection over union) to measure
        how similar two technical specifications are based on shared
        technical terms and concepts.
        
        Args:
            text1 (str): First text to compare
            text2 (str): Second text to compare
            
        Returns:
            float: Similarity score between 0.0 (no similarity) and 1.0 (identical)
        """
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_global_context(self) -> str:
        """
        Get the global context accumulated from all conversations.
        
        Returns the combined technical knowledge from all stored
        conversations, which may be summarized if it exceeds length limits.
        
        Returns:
            str: Global technical specification context
        """
        return self.memory.get('global_context', "")
    
    def clear_memory(self):
        """
        Clear all conversation memory and remove persistent storage.
        
        Resets the memory to initial state and attempts to remove
        the memory file from disk. Useful for starting fresh or
        troubleshooting memory issues.
        """
        self.memory = {
            'conversations': [],
            'global_context': "",
            'last_updated': datetime.now().isoformat(),
            'session_count': 0
        }
        self.save_memory()
        
        # Remove memory file
        try:
            if os.path.exists(self.memory_file):
                os.remove(self.memory_file)
        except Exception as e:
            print(f"Warning: Could not remove memory file: {e}")

class ContextManager:
    """
    Manages technical specification context and intelligent merging.
    
    This class handles the intelligent combination of technical specifications
    from multiple conversations, manages context overflow, and provides
    smart context merging capabilities.
    
    Attributes:
        memory (ConversationMemory): Reference to the conversation memory system
        current_session_id (str): Unique identifier for the current session
    """
    
    def __init__(self, conversation_memory: ConversationMemory):
        """
        Initialize the context manager.
        
        Args:
            conversation_memory (ConversationMemory): Memory system to use for context operations
        """
        self.memory = conversation_memory
        self.current_session_id = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        """
        Generate unique session identifier.
        
        Creates a unique session ID using timestamp and process ID
        to ensure uniqueness across multiple instances and sessions.
        
        Returns:
            str: Unique session identifier
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}_{os.getpid()}"
    
    def merge_contexts(self, current_context: str, new_input: str, 
                      use_global_context: bool = True) -> Tuple[str, List[Dict]]:
        """
        Merge current context with new input and relevant previous contexts.
        
        Intelligently combines the current technical specification context with
        new input and finds relevant previous conversations to enhance the
        specification. Handles context overflow through AI summarization.
        
        Args:
            current_context (str): Existing technical specification context
            new_input (str): New technical specification input to add
            use_global_context (bool): Whether to search for relevant previous contexts
            
        Returns:
            Tuple[str, List[Dict]]: (merged_context, relevant_previous_contexts)
                - merged_context: Combined technical specification
                - relevant_previous_contexts: List of relevant previous conversations
        """
        # Start with current context
        merged_context = current_context if current_context else ""
        
        # Add new input
        if merged_context:
            merged_context += f"\n\nAdditional Context:\n{new_input}"
        else:
            merged_context = new_input
        
        # Get relevant previous contexts
        relevant_contexts = []
        if use_global_context:
            relevant_contexts = self.memory.get_relevant_context(merged_context)
            
            # Add relevant previous contexts
            for ctx in relevant_contexts:
                if ctx['spec_context'] and ctx['spec_context'] not in merged_context:
                    merged_context += f"\n\nRelevant Previous Context:\n{ctx['spec_context']}"
        
        # If merged context is too long, summarize it
        if len(merged_context) > MAX_CONTEXT_LENGTH:
            merged_context = self._summarize_context(merged_context)
        
        return merged_context, relevant_contexts
    
    def _summarize_context(self, context: str) -> str:
        """
        Summarize context while preserving important architectural details.
        
        Uses AI to create a concise summary of technical specifications
        when the combined context exceeds length limits. Preserves key
        architectural information while reducing size.
        
        Args:
            context (str): Technical specification context to summarize
            
        Returns:
            str: Summarized context under length limit
        """
        try:
            llm = api_key_manager.get_chat_openai_instance(model="gpt-4", temperature=0.1)
            
            prompt = f"""
            Summarize the following technical specification while preserving all important architectural details:

            {context}

            Create a concise but comprehensive summary that includes:
            - All system components
            - Key relationships
            - Technology choices
            - External integrations
            - Important architectural decisions

            Keep the summary under {MAX_CONTEXT_LENGTH} characters.
            """
            
            response = llm.invoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            print(f"Warning: Could not summarize context: {e}")
            # Fallback: truncate and keep recent content
            return context[-MAX_CONTEXT_LENGTH:]
    
    def create_conversation_summary(self, spec_context: str, messages: List[Dict], 
                                  result: Optional[Dict] = None) -> Dict:
        """
        Create a summary of the current conversation for memory storage.
        
        Generates a structured summary of the current conversation including
        session metadata, technical specification context, and C4 generation
        results for persistent storage.
        
        Args:
            spec_context (str): Current technical specification context
            messages (List[Dict]): List of chat messages in the conversation
            result (Optional[Dict]): C4 generation result if available
            
        Returns:
            Dict: Structured conversation summary for memory storage
        """
        return {
            'session_id': self.current_session_id,
            'timestamp': datetime.now().isoformat(),
            'spec_context': spec_context,
            'message_count': len(messages),
            'result_summary': self.memory._summarize_result(result) if result else None,
            'context_length': len(spec_context)
        }

class ConversationTab:
    """
    Represents a single conversation tab in the Streamlit UI.
    
    Attributes:
        id (str): Unique identifier for the tab
        title (str): Title of the tab
        messages (List[Dict]): List of chat messages for this tab
        spec_context (str): Current technical specification context for this tab
        current_result (Optional[Dict]): C4 generation result for this tab
    """
    
    def __init__(self, tab_id: str, title: str):
        self.id = tab_id
        self.title = title
        self.messages: List[Dict] = []
        self.spec_context: str = ""
        self.current_result: Optional[Dict] = None

    def get_summary(self) -> Dict:
        """
        Get a summary of the tab's current state.
        
        Returns:
            Dict: Summary of tab info, messages, and context length
        """
        return {
            "tab_id": self.id,
            "title": self.title,
            "message_count": len(self.messages),
            "context_length": len(self.spec_context)
        }

# Initialize session state
def init_session_state():
    """
    Initialize Streamlit session state variables for the chatbot with tab support.
    
    Sets up all necessary session state variables including:
    - Tab management system
    - Chat messages and history for each tab
    - Technical specification context for each tab
    - C4 generation results for each tab
    - Conversation memory system
    - Context management
    - UI state variables
    """
    if "tabs" not in st.session_state:
        st.session_state.tabs = {}
    
    if "active_tab_id" not in st.session_state:
        st.session_state.active_tab_id = None
    
    if "conversation_memory" not in st.session_state:
        st.session_state.conversation_memory = ConversationMemory()
    
    if "context_manager" not in st.session_state:
        st.session_state.context_manager = ContextManager(st.session_state.conversation_memory)
    
    if "output_dir" not in st.session_state:
        st.session_state.output_dir = "generated_c4"
    
    if "show_memory" not in st.session_state:
        st.session_state.show_memory = False
    
    if "relevant_contexts" not in st.session_state:
        st.session_state.relevant_contexts = []
    
    # Create default tab if none exist
    if not st.session_state.tabs:
        create_new_tab("New Chat")
    
    # Set active tab if none is set
    if not st.session_state.active_tab_id:
        st.session_state.active_tab_id = list(st.session_state.tabs.keys())[0]

def create_new_tab(title: str = None) -> str:
    """
    Create a new conversation tab.
    
    Args:
        title (str): Optional title for the tab
        
    Returns:
        str: ID of the newly created tab
    """
    tab_id = str(uuid.uuid4())
    tab_title = title or f"Chat {len(st.session_state.tabs) + 1}"
    
    st.session_state.tabs[tab_id] = ConversationTab(tab_id, tab_title)
    
    # Set as active tab
    st.session_state.active_tab_id = tab_id
    
    return tab_id

def get_active_tab() -> ConversationTab:
    """
    Get the currently active conversation tab.
    
    Returns:
        ConversationTab: The active tab object
    """
    if st.session_state.active_tab_id and st.session_state.active_tab_id in st.session_state.tabs:
        return st.session_state.tabs[st.session_state.active_tab_id]
    
    # Fallback: return first available tab
    if st.session_state.tabs:
        first_tab_id = list(st.session_state.tabs.keys())[0]
        st.session_state.active_tab_id = first_tab_id
        return st.session_state.tabs[first_tab_id]
    
    # Create new tab if none exist
    tab_id = create_new_tab()
    return st.session_state.tabs[tab_id]

def delete_tab(tab_id: str):
    """
    Delete a conversation tab.
    
    Args:
        tab_id (str): ID of the tab to delete
    """
    if tab_id in st.session_state.tabs:
        del st.session_state.tabs[tab_id]
        
        # If we deleted the active tab, switch to another one
        if st.session_state.active_tab_id == tab_id:
            if st.session_state.tabs:
                st.session_state.active_tab_id = list(st.session_state.tabs.keys())[0]
            else:
                st.session_state.active_tab_id = None
        
        # Create a new tab if none exist
        if not st.session_state.tabs:
            create_new_tab()

def render_tab_management():
    """
    Render the tab management interface with ChatGPT-style tabs.
    """
    st.markdown("---")
    
    # Tab creation button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➕ New Chat", type="primary"):
            create_new_tab()
            st.rerun()
    
    with col2:
        st.caption("Create new conversation tabs to work on different technical specifications simultaneously")
    
    # Tab navigation
    if st.session_state.tabs:
        tab_names = []
        tab_ids = []
        
        for tab_id, tab in st.session_state.tabs.items():
            # Create tab name with status indicators
            status_icon = "✅" if tab.current_result else "💬"
            message_count = len(tab.messages)
            tab_name = f"{status_icon} {tab.title}"
            
            if message_count > 0:
                tab_name += f" ({message_count})"
            
            tab_names.append(tab_name)
            tab_ids.append(tab_id)
        
        # Create tabs
        if tab_names:
            selected_tab_index = st.tabs(tab_names)
            
            # Handle tab selection
            for i, tab_id in enumerate(tab_ids):
                if selected_tab_index[i]:
                    if st.session_state.active_tab_id != tab_id:
                        st.session_state.active_tab_id = tab_id
                        st.rerun()
                    
                    # Show tab actions in the selected tab
                    with selected_tab_index[i]:
                        render_tab_actions(tab_id)
                        break
    else:
        st.info("No conversation tabs available. Create a new chat to get started!")

def render_tab_actions(tab_id: str):
    """
    Render actions for a specific tab.
    
    Args:
        tab_id (str): ID of the tab to render actions for
    """
    tab = st.session_state.tabs[tab_id]
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        # Rename tab
        new_title = st.text_input("Tab Title", value=tab.title, key=f"title_{tab_id}")
        if new_title != tab.title:
            tab.title = new_title
            st.rerun()
    
    with col2:
        # Export tab data
        if st.button("📤 Export", key=f"export_{tab_id}"):
            export_tab_data(tab)
    
    with col3:
        # Clear tab
        if st.button("🗑️ Clear", key=f"clear_{tab_id}"):
            tab.messages = []
            tab.spec_context = ""
            tab.current_result = None
            st.rerun()
    
    with col4:
        # Delete tab (if more than one exists)
        if len(st.session_state.tabs) > 1:
            if st.button("❌ Delete", key=f"delete_{tab_id}"):
                delete_tab(tab_id)
                st.rerun()
        else:
            st.caption("Keep at least one tab")

def export_tab_data(tab: ConversationTab):
    """
    Export tab data to a file.
    
    Args:
        tab (ConversationTab): Tab to export
    """
    export_data = {
        "tab_info": tab.get_summary(),
        "messages": tab.messages,
        "spec_context": tab.spec_context,
        "current_result": tab.current_result
    }
    
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_export_{tab.title.replace(' ', '_')}_{timestamp}.json"
    
    # Convert to JSON string
    json_str = json.dumps(export_data, indent=2, default=str)
    
    # Create download button
    st.download_button(
        label="📥 Download Export",
        data=json_str,
        file_name=filename,
        mime="application/json"
    )

def filter_relevant_content(text: str) -> str:
    """
    Filter out content that is not relevant to technical specifications.
    
    Uses AI to intelligently identify and extract only content related to
    software/system architecture, technical requirements, or system design.
    Removes personal conversations, non-technical discussions, and irrelevant
    content to maintain focus on technical specifications.
    
    Args:
        text (str): User input text to filter
        
    Returns:
        str: Filtered text containing only relevant technical content,
             or empty string if no relevant content found
        
    Raises:
        Exception: If AI filtering fails, returns original text as fallback
    """
    try:
        llm = api_key_manager.get_chat_openai_instance(model="gpt-4", temperature=0.1)
        
        prompt = f"""
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
        
        response = llm.invoke(prompt)
        filtered_content = response.content.strip()
        
        if filtered_content == "NO_RELEVANT_CONTENT":
            return ""
        
        return filtered_content
        
    except Exception as e:
        st.error(f"Error filtering content: {e}")
        # If filtering fails, return the original text
        return text

def extract_technical_spec(text: str) -> str:
    """
    Extract technical specification content from user input.
    
    Uses AI to intelligently identify and extract technical architecture
    information from user input, focusing on system components, technology
    choices, data flows, and architectural patterns. Formats the output
    as structured technical specifications suitable for C4 diagram generation.
    
    Args:
        text (str): User input text to extract technical specifications from
        
    Returns:
        str: Structured technical specification content
        
    Raises:
        Exception: If AI extraction fails, returns original text as fallback
    """
    try:
        llm = api_key_manager.get_chat_openai_instance(model="gpt-4", temperature=0.1)
        
        prompt = f"""
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
        
        response = llm.invoke(prompt)
        return response.content.strip()
        
    except Exception as e:
        st.error(f"Error extracting technical spec: {e}")
        return text

def update_spec_context(new_input: str) -> Tuple[str, List[Dict]]:
    """Update technical specification context with new input"""
    active_tab = get_active_tab()
    
    # Use context manager to merge contexts
    merged_context, relevant_contexts = st.session_state.context_manager.merge_contexts(
        active_tab.spec_context, 
        new_input, 
        use_global_context=True
    )
    
    return merged_context, relevant_contexts

def generate_c4_from_context() -> Optional[Dict[str, Any]]:
    """Generate C4 architecture from current context"""
    active_tab = get_active_tab()
    
    if not active_tab.spec_context:
        return None
    
    try:
        with st.spinner("🏗️ Generating C4 Architecture..."):
            result = generate_c4_architecture(active_tab.spec_context)
            return result
    except Exception as e:
        st.error(f"❌ Error generating C4 architecture: {e}")
        return None

def render_chat_interface():
    """Render the main chat interface for the active tab"""
    active_tab = get_active_tab()
    
    st.subheader(f"💬 {active_tab.title} - Technical Specification Chat")
    
    # Chat input
    user_input = st.chat_input("Type your technical specification or ask questions...")
    
    if user_input:
        # Add user message to active tab
        active_tab.messages.append({"role": "user", "content": user_input})
        
        # Filter relevant content
        relevant_content = filter_relevant_content(user_input)
        
        if relevant_content:
            # Extract technical specification
            tech_spec = extract_technical_spec(relevant_content)
            
            # Update context with intelligent merging
            merged_context, relevant_contexts = update_spec_context(tech_spec)
            active_tab.spec_context = merged_context
            
            # Add assistant response
            assistant_response = f"✅ Added to technical specification:\n\n{tech_spec}"
            
            if relevant_contexts:
                assistant_response += f"\n\n🔗 Found {len(relevant_contexts)} relevant previous conversations"
            
            active_tab.messages.append({"role": "assistant", "content": assistant_response})
            
            # Store relevant contexts for display
            st.session_state.relevant_contexts = relevant_contexts
            
            # Auto-generate C4 if context is substantial
            if len(active_tab.spec_context) > 100:
                active_tab.current_result = generate_c4_from_context()
                
                # Save conversation to memory
                if active_tab.current_result:
                    summary = st.session_state.context_manager.create_conversation_summary(
                        active_tab.spec_context,
                        active_tab.messages,
                        active_tab.current_result
                    )
                    st.session_state.conversation_memory.add_conversation(
                        summary['session_id'],
                        active_tab.spec_context,
                        active_tab.messages,
                        active_tab.current_result
                    )
        else:
            # No relevant content found
            active_tab.messages.append({
                "role": "assistant", 
                "content": "❌ No relevant technical content found in your message. Please provide technical specifications, system architecture details, or technology requirements."
            })
    
    # Display chat messages for active tab
    for message in active_tab.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def render_spec_context():
    """Render the current technical specification context for the active tab"""
    active_tab = get_active_tab()
    
    st.subheader("📋 Current Technical Specification")
    
    if active_tab.spec_context:
        with st.expander("View/Edit Specification Context", expanded=True):
            edited_spec = st.text_area(
                "Technical Specification Context",
                value=active_tab.spec_context,
                height=200,
                key=f"spec_editor_{active_tab.id}"
            )
            
            if edited_spec != active_tab.spec_context:
                active_tab.spec_context = edited_spec
                active_tab.current_result = None  # Reset result when spec changes
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔄 Regenerate C4", key=f"regenerate_{active_tab.id}", type="primary"):
                    active_tab.current_result = generate_c4_from_context()
            with col2:
                if st.button("📝 Clear Specification", key=f"clear_spec_{active_tab.id}"):
                    active_tab.spec_context = ""
                    active_tab.current_result = None
                    st.success("✅ Specification cleared")
            with col3:
                if st.button("🧠 Save to Memory", key=f"save_memory_{active_tab.id}"):
                    if active_tab.spec_context:
                        summary = st.session_state.context_manager.create_conversation_summary(
                            active_tab.spec_context,
                            active_tab.messages,
                            active_tab.current_result
                        )
                        st.session_state.conversation_memory.add_conversation(
                            summary['session_id'],
                            active_tab.spec_context,
                            active_tab.messages,
                            active_tab.current_result
                        )
                        st.success("✅ Conversation saved to memory")
    else:
        st.info("💡 Start chatting to build your technical specification!")
        st.caption("The specification will be built automatically as you provide technical details")

def render_c4_results():
    """Render C4 generation results for the active tab"""
    active_tab = get_active_tab()
    
    st.subheader("🏗️ C4 Architecture Results")
    
    if active_tab.current_result and active_tab.current_result.get("success"):
        result = active_tab.current_result
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Unified View", 
            "🌐 System Context", 
            "📦 Container", 
            "🔧 Component",
            "👥 User-Centric"
        ])
        
        with tab1:
            st.subheader("📊 Unified Architecture View")
            if result.get("summary"):
                st.write(result["summary"])
            
            # Display architecture elements
            col1, col2 = st.columns(2)
            
            with col1:
                if result.get("systems"):
                    st.write("**Systems:**")
                    for system in result["systems"]:
                        st.write(f"- {system.get('name', 'Unknown')}: {system.get('description', 'No description')}")
                
                if result.get("containers"):
                    st.write("**Containers:**")
                    for container in result["containers"]:
                        st.write(f"- {container.get('name', 'Unknown')}: {container.get('description', 'No description')}")
            
            with col2:
                if result.get("components"):
                    st.write("**Components:**")
                    for component in result["components"]:
                        st.write(f"- {component.get('name', 'Unknown')}: {component.get('description', 'No description')}")
                
                if result.get("relationships"):
                    st.write("**Relationships:**")
                    for rel in result["relationships"][:5]:  # Show first 5
                        st.write(f"- {rel.get('source', 'Unknown')} → {rel.get('destination', 'Unknown')}")
        
        with tab2:
            st.subheader("🌐 System Context DSL")
            if result.get("dsl", {}).get("context"):
                st.code(result["dsl"]["context"], language="text")
            else:
                st.info("No system context DSL generated yet")
        
        with tab3:
            st.subheader("📦 Container DSL")
            if result.get("dsl", {}).get("container"):
                st.code(result["dsl"]["container"], language="text")
            else:
                st.info("No container DSL generated yet")
        
        with tab4:
            st.subheader("🔧 Component DSL")
            if result.get("dsl", {}).get("component"):
                st.code(result["dsl"]["component"], language="text")
            else:
                st.info("No component DSL generated yet")
        
        with tab5:
            st.subheader("👥 User-Centric DSL")
            if result.get("dsl", {}).get("user_centric"):
                st.code(result["dsl"]["user_centric"], language="text")
            else:
                st.info("No user-centric DSL generated yet")
        
        # Export and save options
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("💾 Save DSL Files", key=f"save_dsl_{active_tab.id}"):
                try:
                    saved_files = save_dsl_files(result, st.session_state.output_dir)
                    st.success(f"✅ Saved {len(saved_files)} files to {st.session_state.output_dir}")
                except Exception as e:
                    st.error(f"❌ Error saving files: {e}")
        
        with col2:
            if st.button("📥 Download JSON", key=f"download_json_{active_tab.id}"):
                json_str = json.dumps(result, indent=2, default=str)
                st.download_button(
                    label="📥 Download",
                    data=json_str,
                    file_name=f"c4_architecture_{active_tab.title.replace(' ', '_')}.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("🔄 Regenerate", key=f"regenerate_c4_{active_tab.id}"):
                active_tab.current_result = generate_c4_from_context()
                st.rerun()
    
    elif active_tab.current_result and not active_tab.current_result.get("success"):
        st.error("❌ C4 Generation Failed")
        st.write(f"Error: {active_tab.current_result.get('error', 'Unknown error')}")
        
        if st.button("🔄 Retry", key=f"retry_{active_tab.id}"):
            active_tab.current_result = generate_c4_from_context()
            st.rerun()
    
    else:
        st.info("💡 No C4 architecture generated yet. Build your technical specification first!")

def render_relevant_contexts():
    """Render relevant previous contexts for the active tab"""
    active_tab = get_active_tab()
    
    if st.session_state.relevant_contexts:
        st.subheader("🔗 Relevant Previous Contexts")
        
        for i, context in enumerate(st.session_state.relevant_contexts):
            with st.expander(f"📋 Context {i+1} (Similarity: {context.get('similarity', 0):.2f})"):
                st.write(f"**Timestamp:** {context.get('timestamp', 'Unknown')}")
                st.write(f"**Context Length:** {context.get('context_length', 0)} characters")
                
                if context.get('spec_context'):
                    st.write("**Technical Specification:**")
                    st.text_area(
                        f"Context {i+1}",
                        value=context['spec_context'],
                        height=100,
                        key=f"context_{i}_{active_tab.id}",
                        disabled=True
                    )
                
                if context.get('result_summary'):
                    st.write("**Previous Result Summary:**")
                    st.json(context['result_summary'])

def render_sidebar():
    """
    Render the sidebar with chatbot controls and information.
    
    Creates a comprehensive sidebar containing:
    - API key status and configuration
    - Memory management controls
    - Output directory settings
    - File save/export functionality
    - Conversation management tools
    
    The sidebar provides easy access to all chatbot configuration
    and management features while keeping the main interface clean.
    """
    st.sidebar.header("🤖 Chatbot Controls")
    
    # API key status
    api_status = api_key_manager.get_api_key_status()
    
    if api_status["available"]:
        if api_status["validation"]["valid"]:
            st.sidebar.success(api_key_manager.get_api_key_display_info())
            
            # Show additional API key info in expander
            with st.sidebar.expander("🔑 API Key Details"):
                st.info(f"**Source:** {', '.join(api_status['sources'])}")
                st.info(f"**Key Length:** {api_status['key_length']} characters")
                if api_status['key_prefix']:
                    st.info(f"**Key Prefix:** {api_status['key_prefix']}")
                
                # Refresh button
                if st.button("🔄 Refresh API Key", key="refresh_api_key"):
                    api_key_manager.refresh_api_key()
                    st.success("✅ API Key refreshed")
                    st.rerun()
        else:
            st.sidebar.warning(f"⚠️ API Key Issue: {api_status['validation']['error']}")
    else:
        st.sidebar.error("❌ OpenAI API Key Missing")
        
        # Show setup instructions
        with st.sidebar.expander("📋 Setup Instructions"):
            st.markdown(api_key_manager.get_setup_instructions())
    
    st.sidebar.divider()
    
    # Memory management
    st.sidebar.subheader("🧠 Memory Management")
    
    if st.sidebar.button("📊 Show Memory Stats"):
        st.session_state.show_memory = not st.session_state.show_memory
    
    memory = st.session_state.conversation_memory
    st.sidebar.info(f"💾 Stored conversations: {len(memory.memory['conversations'])}")
    st.sidebar.info(f"🌐 Global context: {len(memory.get_global_context())} chars")
    
    if st.sidebar.button("🗑️ Clear Memory"):
        memory.clear_memory()
        st.session_state.spec_context = ""
        st.session_state.current_result = None
        st.sidebar.success("✅ Memory cleared")
    
    st.sidebar.divider()
    
    # Output directory
    st.session_state.output_dir = st.sidebar.text_input(
        "📁 Output Directory", 
        value=st.session_state.output_dir
    )
    
    # Save results button
    if st.sidebar.button("💾 Save Current DSLs", type="primary"):
        if st.session_state.current_result and st.session_state.current_result.get("success"):
            try:
                files = save_dsl_files(st.session_state.current_result, st.session_state.output_dir)
                st.sidebar.success(f"✅ Saved {len(files)} files")
            except Exception as e:
                st.sidebar.error(f"❌ Save failed: {e}")
        else:
            st.sidebar.warning("⚠️ No successful generation to save")
    
    # Clear conversation
    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.spec_context = ""
        st.session_state.current_result = None
        st.session_state.chat_history = []
        st.sidebar.success("✅ Conversation cleared")
    
    # Export conversation
    if st.sidebar.button("📤 Export Conversation"):
        if st.session_state.chat_history:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            
            export_data = {
                "timestamp": timestamp,
                "spec_context": st.session_state.spec_context,
                "chat_history": st.session_state.chat_history,
                "result": st.session_state.current_result,
                "memory_stats": {
                    "total_conversations": len(memory.memory['conversations']),
                    "global_context_length": len(memory.get_global_context())
                }
            }
            
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=filename,
                mime="application/json"
            )

def render_memory_stats():
    """Render memory statistics and relevant contexts"""
    if not st.session_state.show_memory:
        return
    
    st.subheader("🧠 Memory Statistics")
    
    memory = st.session_state.conversation_memory
    mem_data = memory.memory
    
    # Memory overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Conversations", len(mem_data['conversations']))
    with col2:
        st.metric("Global Context", f"{len(mem_data.get('global_context', ''))} chars")
    with col3:
        last_updated = mem_data.get('last_updated', 'Unknown')
        if last_updated != 'Unknown':
            last_updated = datetime.fromisoformat(last_updated).strftime("%Y-%m-%d %H:%M")
        st.metric("Last Updated", last_updated)
    
    # Recent conversations
    if mem_data['conversations']:
        st.subheader("📚 Recent Conversations")
        recent_convs = mem_data['conversations'][-10:]  # Show last 10
        
        for conv in reversed(recent_convs):
            with st.expander(f"💬 {conv['id']} - {conv['timestamp'][:10]}"):
                st.write(f"**Message Count:** {conv['message_count']}")
                st.write(f"**Context Length:** {len(conv['spec_context'])} chars")
                if conv['result_summary']:
                    st.write("**Result:**")
                    st.json(conv['result_summary'])
                
                if st.button(f"Load Context {conv['id']}", key=f"load_{conv['id']}"):
                    st.session_state.spec_context = conv['spec_context']
                    st.session_state.current_result = None
                    st.success(f"✅ Loaded conversation {conv['id']}")
                    st.rerun()
    
    # Global context
    global_context = memory.get_global_context()
    if global_context:
        st.subheader("🌐 Global Context")
        with st.expander("View Global Context"):
            st.text_area("Global Context", global_context, height=200, disabled=True)
            
            if st.button("Use Global Context"):
                st.session_state.spec_context = global_context
                st.session_state.current_result = None
                st.success("✅ Loaded global context")
                st.rerun()

def render_examples():
    """Render example technical specifications"""
    st.subheader("💡 Example Technical Specifications")
    
    examples = [
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
        }
    ]
    
    for i, example in enumerate(examples):
        with st.expander(f"📋 {example['title']} - {example['description']}"):
            st.write(example['spec'])
            if st.button(f"Use Example {i+1}", key=f"example_{i}"):
                st.session_state.spec_context = example['spec'].strip()
                st.session_state.current_result = None
                st.success(f"✅ Loaded {example['title']} example")
                st.rerun()

def render_api_key_status():
    """
    Render API key status information in the main interface.
    
    Shows current API key status, source information, and setup instructions
    if the key is missing or invalid.
    """
    st.markdown("---")
    
    # API Key Status Section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🔑 API Key Status")
        
        api_status = api_key_manager.get_api_key_status()
        
        if api_status["available"]:
            if api_status["validation"]["valid"]:
                st.success(api_key_manager.get_api_key_display_info())
                
                # Show key details
                with st.expander("📊 Key Information"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Status", "✅ Valid")
                        st.metric("Source", ", ".join(api_status["sources"]))
                    with col_b:
                        st.metric("Length", f"{api_status['key_length']} chars")
                        if api_status["key_prefix"]:
                            st.metric("Prefix", api_status["key_prefix"])
            else:
                st.warning(f"⚠️ API Key Issue: {api_status['validation']['error']}")
                st.info("Please check your API key configuration.")
        else:
            st.error("❌ OpenAI API Key Not Available")
            
            # Show setup instructions
            with st.expander("📋 Setup Instructions", expanded=True):
                st.markdown(api_key_manager.get_setup_instructions())
                
                # Quick setup options
                st.subheader("🚀 Quick Setup")
                
                col_x, col_y = st.columns(2)
                with col_x:
                    if st.button("🔄 Refresh API Key", key="main_refresh_api"):
                        api_key_manager.refresh_api_key()
                        st.success("✅ API Key refreshed")
                        st.rerun()
                
                with col_y:
                    if st.button("📖 View Documentation", key="view_docs"):
                        st.info("Check the sidebar for detailed API key management options.")
    
    with col2:
        # API Key Health Indicator
        st.subheader("🏥 Health Check")
        
        if check_api_key_availability():
            st.success("✅ Healthy")
            st.metric("Status", "Ready")
        else:
            st.error("❌ Unhealthy")
            st.metric("Status", "Not Ready")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔍 Check Status", key="check_status"):
            st.rerun()
        
        if st.button("📋 Show Details", key="show_details"):
            st.info("Expand the API Key Status section above for detailed information.")

def main():
    """
    Main application function for the C4 Architecture Generator Chatbot with tab support.
    
    Sets up the Streamlit page configuration, initializes the application
    state, and renders the complete chatbot interface including:
    - Page title and configuration
    - Tab management system
    - Session state initialization
    - Sidebar with controls
    - Main chat interface
    - Technical specification context
    - C4 generation results
    - Examples and memory statistics
    
    The interface now supports multiple concurrent conversations in tabs
    for better organization and productivity.
    """
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title(APP_TITLE)
    st.caption("🤖 Chat with me to build technical specifications and generate C4 architecture diagrams!")
    
    # Initialize session state
    init_session_state()
    
    # Render tab management
    render_tab_management()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    st.markdown("---")
    
    # API Key Status
    render_api_key_status()

    # Chat interface
    render_chat_interface()
    
    # Relevant contexts (if any)
    render_relevant_contexts()
    
    # Specification context
    render_spec_context()
    
    # C4 Results
    render_c4_results()
    
    # Examples and additional info
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_examples()
    
    with col2:
        render_memory_stats()
        
        # Current tab info
        active_tab = get_active_tab()
        st.subheader("📊 Current Tab Information")
        st.info(f"**Active Tab:** {active_tab.title}")
        st.info(f"📝 Specification length: {len(active_tab.spec_context)} characters")
        st.info(f"💬 Messages: {len(active_tab.messages)}")
        if active_tab.current_result:
            st.success("✅ C4 Architecture available")
        else:
            st.warning("⚠️ No technical specification yet")

if __name__ == "__main__":
    main()
