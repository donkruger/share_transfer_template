# app/pages/6_Beneficial_Owners.py (Simplified)

import streamlit as st
import sys
from pathlib import Path

# --- Setup ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.components.sidebar import render_sidebar
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS
from app.utils import (
    repeat_prefix, 
    initialize_state,
    persist_text_input,
    persist_number_input,
    persist_selectbox,
    persist_file_uploader
)



# --- INITIALIZE STATE ---
initialize_state()

st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)
render_sidebar()

# --- Page Content ---
st.header("6. Beneficial Owners")

st.subheader(">5% Ultimate Beneficial Owner (UBO)")
persist_number_input("Number of beneficial owners (>5%)", "n_ubo", min_value=0, step=1)

for i in range(st.session_state.n_ubo):
    with st.expander(repeat_prefix(i, "Beneficial owner")):
        persist_selectbox("Holder type", f"ubo_type_{i}", options=["Natural Person", "Juristic Person"])
        persist_text_input("Legal / Full name", f"ubo_full_{i}")
        persist_text_input("ID / Registration number", f"ubo_id_{i}")
        persist_file_uploader("Upload Identity Document", f"ubo_id_doc_{i}") 