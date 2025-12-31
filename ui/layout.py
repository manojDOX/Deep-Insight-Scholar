import streamlit as st

from ui.dashboard import render_dashboard
from ui.chat import render_chat
from ui.Trends_And_Citations import render_trends_and_citations
from core.vector_store import VectorStoreManager
from pathlib import Path
import streamlit as st


def init_vector_store():
    """
    Initialize the vector store and load it into Streamlit's session state if not already present

    Args:
          No arguments
    Returns:
          None
    """
    if "vector_store" in st.session_state:
        return

    faiss_path = Path("data/faiss_index")
    if not faiss_path.exists():
        st.warning("⚠️ Vector store not found. Ask admin to run prepare_pdf.py.")
        return

    vs = VectorStoreManager()
    try:
        vs.load()
        st.session_state.vector_store = vs
    except Exception as e:
        st.error(f"Failed to load vector store: {e}")


def render_layout():
    """
    Configure the Streamlit page layout and render the main application tabs

    Args:
          No arguments
    Returns:
          None
    """
    st.set_page_config(
        page_title="Deep Insight Scholar",
        layout="wide"
    )
    init_vector_store()
    st.title("📘 Deep Insight Scholar")

    tab1, tab2, tab3 = st.tabs([
        "📚 Paper Library",
        "💬 Chat Assistant",
        "📈 Trend Analysis"
    ])

    with tab1:
        render_dashboard()

    with tab2:
        render_chat(scoped=False)

    with tab3:
        render_trends_and_citations()