# app/pages/2_Business_Information.py (Simplified)

import streamlit as st
import sys
from pathlib import Path

# --- Setup ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.components.sidebar import render_sidebar
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS
from app.utils import (
    initialize_state,
    persist_text_input,
    persist_number_input,
    persist_text_area,
    persist_file_uploader
)



# --- INITIALIZE STATE ---
initialize_state()

st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)
render_sidebar()

# --- Page Content ---
st.header("2. Business Information")

persist_text_input("Registered legal name", "reg_name")
persist_text_input("Trading name (if different from registered name)", "trading_name")
persist_text_input("Registration number", "reg_no")
persist_text_input("FSP number", "fsp_no")
persist_number_input(
    "Total assets under management (ZAR)", "aum", min_value=0.0, step=1000.0, format="%.2f"
)
persist_text_area("Physical address", "phys_addr")

st.markdown("---")
st.markdown("##### Mandatory Document Uploads")

st.markdown("**Company Incorporation Documentation**")
persist_file_uploader(
    "Upload either (CM1 & CM2), (COR14.3 & COR15.3), or your latest CIPC Disclosure Certificate.",
    "inc_docs", accept_multiple_files=True
)
st.markdown("**Company Registered Address**")
persist_file_uploader(
    "Upload either (CM22), (COR14.3 or COR21), or your latest CIPC Disclosure Certificate.",
    "addr_docs", accept_multiple_files=True
)
st.markdown("**Proof of Physical / Operating Address**")
persist_file_uploader(
    "Upload a recent (less than 3 months old) utility bill, telephone account, bank statement etc.",
    "poa_doc"
) 