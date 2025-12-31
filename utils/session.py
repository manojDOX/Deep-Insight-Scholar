import streamlit as st

def init_session():
    """
    Initialize Streamlit session state variables for the application

    Args:
          No arguments
    Returns:
          None
    """
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None

    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = None

    if "papers_loaded" not in st.session_state:
        st.session_state.papers_loaded = False

    if "selected_paper" not in st.session_state:
        st.session_state.selected_paper = None

    if "messages" not in st.session_state:
        st.session_state.messages = []