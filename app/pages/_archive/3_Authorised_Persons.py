# app/pages/3_Authorised_Persons.py (Simplified)

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
    persist_file_uploader
)



# --- INITIALIZE STATE ---
initialize_state()

st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)
render_sidebar()

# --- Page Content ---
st.header("3. Authorised Persons")

persist_number_input("Number of authorised persons", "n_auth", min_value=1, step=1)

for i in range(st.session_state.n_auth):
    with st.expander(repeat_prefix(i, "Authorised person")):
        persist_text_input("Full name", f"auth_full_{i}")
        persist_text_input("ID/Passport number", f"auth_id_{i}")
        persist_text_input("Telephone number", f"auth_tel_{i}")
        persist_text_input("Email address", f"auth_em_{i}")
        persist_file_uploader("Upload ID / Passport Document", f"auth_id_doc_{i}")
        persist_file_uploader("Upload Proof of Address", f"auth_poa_doc_{i}") 