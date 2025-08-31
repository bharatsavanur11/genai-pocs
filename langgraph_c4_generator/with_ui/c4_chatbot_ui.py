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
                    llm = ChatOpenAI(
                        model="gpt-4", 
                        api_key=os.getenv("OPENAI_API_KEY"), 
                        temperature=0.1
                    )
                    
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
            llm = ChatOpenAI(
                model="gpt-4", 
                api_key=os.getenv("OPENAI_API_KEY"), 
                temperature=0.1
            )
            
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

# Initialize session state
def init_session_state():
    """
    Initialize Streamlit session state variables for the chatbot.
    
    Sets up all necessary session state variables including:
    - Chat messages and history
    - Technical specification context
    - C4 generation results
    - Conversation memory system
    - Context management
    - UI state variables
    
    This function ensures all required state variables exist
    before the chatbot interface is rendered.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "spec_context" not in st.session_state:
        st.session_state.spec_context = ""
    if "current_result" not in st.session_state:
        st.session_state.current_result = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "output_dir" not in st.session_state:
        st.session_state.output_dir = "generated_c4"
    if "conversation_memory" not in st.session_state:
        st.session_state.conversation_memory = ConversationMemory()
    if "context_manager" not in st.session_state:
        st.session_state.context_manager = ContextManager(st.session_state.conversation_memory)
    if "show_memory" not in st.session_state:
        st.session_state.show_memory = False
    if "relevant_contexts" not in st.session_state:
        st.session_state.relevant_contexts = []

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
        llm = ChatOpenAI(
            model="gpt-4", 
            api_key=os.getenv("OPENAI_API_KEY"), 
            temperature=0.1
        )
        
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
        llm = ChatOpenAI(
            model="gpt-4", 
            api_key=os.getenv("OPENAI_API_KEY"), 
            temperature=0.1
        )
        
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
    """
    Update the technical specification context with new input.
    
    Intelligently merges new technical specification input with existing
    context using the ContextManager. Automatically finds relevant previous
    conversations and combines them to build comprehensive specifications.
    
    Args:
        new_input (str): New technical specification input to add
        
    Returns:
        Tuple[str, List[Dict]]: (merged_context, relevant_contexts)
            - merged_context: Combined technical specification context
            - relevant_contexts: List of relevant previous conversations found
            
    Note:
        This function automatically updates the session state with relevant
        contexts for display in the UI.
    """
    context_manager = st.session_state.context_manager
    current_context = st.session_state.spec_context
    
    # Merge contexts intelligently
    merged_context, relevant_contexts = context_manager.merge_contexts(
        current_context, new_input, use_global_context=True
    )
    
    # Store relevant contexts for display
    st.session_state.relevant_contexts = relevant_contexts
    
    return merged_context, relevant_contexts

def generate_c4_from_context() -> Optional[Dict[str, Any]]:
    """
    Generate C4 architecture from the current specification context.
    
    Uses the current technical specification context stored in session state
    to generate C4 architecture diagrams. Displays a loading spinner during
    generation and handles errors gracefully.
    
    Returns:
        Optional[Dict[str, Any]]: C4 generation result dictionary if successful,
                                  None if no context available or generation fails
        
    Note:
        This function requires a valid technical specification context to be
        present in st.session_state.spec_context.
    """
    if not st.session_state.spec_context.strip():
        return None
    
    try:
        with st.spinner("🤖 Generating C4 Architecture..."):
            result = generate_c4_architecture(st.session_state.spec_context)
            return result
    except Exception as e:
        st.error(f"Error generating C4 architecture: {e}")
        return None

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
    api_present = bool(os.getenv("OPENAI_API_KEY"))
    if api_present:
        st.sidebar.success("✅ OpenAI API Key Detected")
    else:
        st.sidebar.error("❌ OpenAI API Key Missing")
        st.sidebar.info("Set OPENAI_API_KEY in your environment or .env file")
    
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

def render_relevant_contexts():
    """Render relevant previous contexts"""
    if not st.session_state.relevant_contexts:
        return
    
    st.subheader("🔗 Relevant Previous Contexts")
    st.info("The following previous conversations were found to be relevant to your current specification:")
    
    for i, ctx in enumerate(st.session_state.relevant_contexts):
        with st.expander(f"📋 {ctx['id']} (Similarity: {ctx['similarity']:.2f})"):
            st.write(f"**Timestamp:** {ctx['timestamp']}")
            st.write(f"**Message Count:** {ctx['message_count']}")
            st.write(f"**Context:** {ctx['spec_context'][:200]}...")
            
            if st.button(f"Append Context {i+1}", key=f"append_{i}"):
                current_spec = st.session_state.spec_context
                if current_spec:
                    st.session_state.spec_context = f"{current_spec}\n\nAppended Context:\n{ctx['spec_context']}"
                else:
                    st.session_state.spec_context = ctx['spec_context']
                
                st.session_state.current_result = None
                st.success(f"✅ Appended relevant context from {ctx['id']}")
                st.rerun()

def render_chat_interface():
    """Render the main chat interface"""
    st.subheader("💬 Technical Specification Chat")
    
    # Chat input
    user_input = st.chat_input("Type your technical specification or ask questions...")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Filter relevant content
        relevant_content = filter_relevant_content(user_input)
        
        if relevant_content:
            # Extract technical specification
            tech_spec = extract_technical_spec(relevant_content)
            
            # Update context with intelligent merging
            merged_context, relevant_contexts = update_spec_context(tech_spec)
            st.session_state.spec_context = merged_context
            
            # Add assistant response
            assistant_response = f"✅ Added to technical specification:\n\n{tech_spec}"
            
            if relevant_contexts:
                assistant_response += f"\n\n🔗 Found {len(relevant_contexts)} relevant previous conversations"
            
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
            # Store in chat history
            st.session_state.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "relevant_content": relevant_content,
                "tech_spec": tech_spec,
                "merged_context": merged_context
            })
            
            # Auto-generate C4 if context is substantial
            if len(st.session_state.spec_context) > 100:
                st.session_state.current_result = generate_c4_from_context()
                
                # Save conversation to memory
                if st.session_state.current_result:
                    summary = st.session_state.context_manager.create_conversation_summary(
                        st.session_state.spec_context,
                        st.session_state.messages,
                        st.session_state.current_result
                    )
                    st.session_state.conversation_memory.add_conversation(
                        summary['session_id'],
                        st.session_state.spec_context,
                        st.session_state.messages,
                        st.session_state.current_result
                    )
        else:
            # No relevant content found
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "❌ No relevant technical content found in your message. Please provide technical specifications, system architecture details, or technology requirements."
            })
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def render_spec_context():
    """Render the current technical specification context"""
    st.subheader("📋 Current Technical Specification")
    
    if st.session_state.spec_context:
        with st.expander("View/Edit Specification Context", expanded=True):
            edited_spec = st.text_area(
                "Technical Specification Context",
                value=st.session_state.spec_context,
                height=200,
                key="spec_editor"
            )
            
            if edited_spec != st.session_state.spec_context:
                st.session_state.spec_context = edited_spec
                st.session_state.current_result = None  # Reset result when spec changes
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔄 Regenerate C4", type="primary"):
                    st.session_state.current_result = generate_c4_from_context()
            with col2:
                if st.button("📝 Clear Specification"):
                    st.session_state.spec_context = ""
                    st.session_state.current_result = None
                    st.success("✅ Specification cleared")
            with col3:
                if st.button("🧠 Save to Memory"):
                    if st.session_state.spec_context:
                        summary = st.session_state.context_manager.create_conversation_summary(
                            st.session_state.spec_context,
                            st.session_state.messages,
                            st.session_state.current_result
                        )
                        st.session_state.conversation_memory.add_conversation(
                            summary['session_id'],
                            st.session_state.spec_context,
                            st.session_state.messages,
                            st.session_state.current_result
                        )
                        st.success("✅ Saved to conversation memory")
                    else:
                        st.warning("⚠️ No specification to save")
    else:
        st.info("💡 Start by providing technical specifications in the chat above!")

def render_c4_results():
    """Render the C4 architecture generation results"""
    st.subheader("🏗️ Generated C4 Architecture")
    
    if not st.session_state.current_result:
        st.info("🤖 Generate C4 architecture by providing technical specifications in the chat above")
        return
    
    result = st.session_state.current_result
    
    if not result.get("success"):
        st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
        return
    
    # Success message
    st.success("✅ C4 Architecture generated successfully!")
    
    # Summary
    with st.expander("📊 Architecture Summary", expanded=True):
        summary = result.get("summary", "No summary available")
        st.write(summary)
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Systems", len(result.get("systems", [])))
        with col2:
            st.metric("Containers", len(result.get("containers", [])))
        with col3:
            st.metric("Components", len(result.get("components", [])))
        with col4:
            st.metric("Relationships", len(result.get("relationships", [])))
    
    # DSL Tabs
    dsl = result.get("dsl", {})
    tabs = st.tabs([
        "🌐 Unified (Context+Container)", 
        "🏢 System Context", 
        "📦 Container", 
        "🔧 Component", 
        "📄 JSON Data"
    ])
    
    with tabs[0]:
        cc = dsl.get("context_container")
        if cc:
            st.code(cc, language="dsl")
            st.caption("Unified Context + Container DSL")
        else:
            st.info("Unified DSL not available yet")
    
    with tabs[1]:
        ctx = dsl.get("context")
        if ctx:
            st.code(ctx, language="dsl")
            st.caption("System Context DSL")
        else:
            st.info("Context DSL not available")
    
    with tabs[2]:
        cont = dsl.get("container")
        if cont:
            st.code(cont, language="dsl")
            st.caption("Container DSL")
        else:
            st.info("Container DSL not available")
    
    with tabs[3]:
        comp = dsl.get("component")
        if comp:
            st.code(comp, language="dsl")
            st.caption("Component DSL")
        else:
            st.info("Component DSL not available")
    
    with tabs[4]:
        st.json({
            "systems": result.get("systems", []),
            "containers": result.get("containers", []),
            "components": result.get("components", []),
            "relationships": result.get("relationships", []),
            "external_systems": result.get("external_systems", []),
            "missing_info": result.get("missing_info", [])
        })

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

def main():
    """
    Main application function for the C4 Architecture Generator Chatbot.
    
    Sets up the Streamlit page configuration, initializes the application
    state, and renders the complete chatbot interface including:
    - Page title and configuration
    - Session state initialization
    - Sidebar with controls
    - Main chat interface
    - Technical specification context
    - C4 generation results
    - Examples and memory statistics
    
    The interface is organized in a two-column layout for optimal
    user experience and efficient use of screen space.
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
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        render_chat_interface()
        
        # Relevant contexts (if any)
        render_relevant_contexts()
        
        # Specification context
        render_spec_context()
        
        # C4 Results
        render_c4_results()
    
    with col2:
        # Examples
        render_examples()
        
        # Memory stats
        render_memory_stats()
        
        # Current context info
        st.subheader("📊 Context Information")
        if st.session_state.spec_context:
            st.info(f"📝 Specification length: {len(st.session_state.spec_context)} characters")
            st.info(f"💬 Messages: {len(st.session_state.messages)}")
            if st.session_state.current_result:
                st.success("✅ C4 Architecture available")
        else:
            st.warning("⚠️ No technical specification yet")

if __name__ == "__main__":
    main()
