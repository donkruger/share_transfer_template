# app/pages/5_Director_Information.py (Simplified)

import streamlit as st
import sys
from pathlib import Path
import datetime

# --- Setup ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.components.sidebar import render_sidebar
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS
from app.utils import (
    repeat_prefix, 
    initialize_state,
    persist_text_input,
    persist_number_input,
    persist_date_input,
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
st.header("5. Director Information")

persist_number_input("Number of directors", "n_dir", min_value=1, step=1)

for i in range(st.session_state.n_dir):
    with st.expander(repeat_prefix(i, "Director")):
        persist_text_input("Full name & surname", f"dir_full_{i}")
        persist_text_input("Identity/Passport number", f"dir_id_{i}")
        persist_date_input("Date appointed", f"dir_date_{i}")
        persist_selectbox("Executive status", f"dir_exec_{i}", options=["Executive", "Non-Executive"])
        persist_text_input("Email address", f"dir_email_{i}")
        persist_file_uploader("Upload ID / Passport Document", f"dir_id_doc_{i}") 