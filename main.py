import streamlit as st
from utils.session import init_session
from ui.layout import render_layout

st.set_page_config(
    page_title="Research Paper Intelligence System",
    layout="wide"
)

init_session()
render_layout()
