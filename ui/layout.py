import streamlit as st
from ui.ingestion import render_ingestion
from ui.dashboard import render_dashboard
from ui.chat import render_chat

def render_layout():
    st.sidebar.title("📘 Research Assistant")

    section = st.sidebar.radio(
        "Navigate",
        ["Load Papers", "Paper Library", "Chat Assistant"]
    )

    if section == "Load Papers":
        render_ingestion()
    elif section == "Paper Library":
        render_dashboard()
    else:
        render_chat()
