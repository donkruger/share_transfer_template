# app/pages/4_Financial_Matters.py (Simplified)

import streamlit as st
import sys
from pathlib import Path

# --- Setup ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.components.sidebar import render_sidebar
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS
from app.utils import initialize_state, persist_file_uploader



# --- INITIALIZE STATE ---
initialize_state()

st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)
render_sidebar()

# --- Page Content ---
st.header("4. Financial Matters")

persist_file_uploader("Confirmation of bank account", "bank", type=["pdf", "png", "jpg"])
persist_file_uploader("SARS tax clearance certificate", "sars", type=["pdf", "png", "jpg"])
persist_file_uploader("Latest audited financial statements", "financials", type=["pdf"]) 