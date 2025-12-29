"""
UI Components Module
====================
DAY 4: Reusable Streamlit components.

SOLID Principle: Single Responsibility Principle (SRP)
- Each component has ONE job

Topics to teach:
- Streamlit components
- Reusability
- Session state management
- File upload handling
"""

import streamlit as st
from typing import List, Optional
import tempfile
import os


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "vector_store_initialized" not in st.session_state:
        st.session_state.vector_store_initialized = False
    
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []


def display_chat_history():
    """Display all messages in the chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message.get("sources"):
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.write(f"- {source}")


def add_message(role: str, content: str, sources: List[str] = None):
    """
    Add a message to chat history.
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
        sources: Optional list of source documents
    """
    message = {"role": role, "content": content}
    if sources:
        message["sources"] = sources
    st.session_state.messages.append(message)


def clear_chat_history():
    """Clear all messages from chat history."""
    st.session_state.messages = []


def save_uploaded_file(uploaded_file) -> str:
    """
    Save an uploaded file to a temporary location.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Path to the saved file
    """
    # Create temp directory if it doesn't exist
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


def display_sidebar_info():
    """Display information in the sidebar."""
    with st.sidebar:
        st.header("📖 About")
        st.markdown("""
        This is a **AI Advocte RAG Chatbot** that can:
        - 📄 Answer questions from your documents
        - 🔍 Search the web using Tavily
        - 💬 Have natural conversations
        
        **How to use:**
        1. Upload PDF or TXT files
        2. Wait for processing
        3. Ask questions!
        """)
        
        st.divider()
        
        # Show upload status
        st.header("📁 Uploaded Files")
        if st.session_state.uploaded_files:
            for file in st.session_state.uploaded_files:
                st.write(f"✅ {file}")
        else:
            st.write("No files uploaded yet")
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            clear_chat_history()
            st.rerun()


def display_file_uploader():
    """Display file upload widget and return uploaded files."""
    uploaded_files = st.file_uploader(
        "Upload your documents (PDF or TXT)",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help="Upload documents to chat with"
    )
    return uploaded_files


def display_processing_status(message: str, status: str = "info"):
    """
    Display a status message.
    
    Args:
        message: Status message
        status: Type - 'info', 'success', 'warning', 'error'
    """
    if status == "success":
        st.success(message)
    elif status == "warning":
        st.warning(message)
    elif status == "error":
        st.error(message)
    else:
        st.info(message)


def create_web_search_toggle() -> bool:
    """Create a toggle for web search."""
    return st.toggle(
        "🌐 Enable Web Search",
        value=False,
        help="When enabled, the chatbot will also search the web for answers"
    )