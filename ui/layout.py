import streamlit as st
from ui.ingestion import render_ingestion
from ui.dashboard import render_dashboard
from ui.chat import render_chat

def render_layout():
    st.title("📘 Research Assistant")

    tab1, tab2, tab3 = st.tabs([
        "📥 Load Papers",
        "📚 Paper Library",
        "💬 Chat Assistant"
    ])

    with tab1:
        render_ingestion()

    with tab2:
        render_dashboard()

    with tab3:
        render_chat()

