# app/pages/7_Strategic_Considerations.py (Simplified)

import streamlit as st
import sys
from pathlib import Path

# --- Setup ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.components.sidebar import render_sidebar
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS
from app.utils import (
    initialize_state,
    persist_text_area,
    persist_number_input,
    persist_text_input,
    persist_file_uploader
)



# --- INITIALIZE STATE ---
initialize_state()

st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)
render_sidebar()

# --- Page Content ---
st.header("7. Strategic Considerations")

st.subheader("Investment Manager Strategic Considerations")
persist_text_area("Please provide us with an overview of your business; its history, process, and philosophy.", "bus_overview")
persist_text_area("Provide a detailed description of the investment philosophy and how it guides portfolio construction and security selection.", "inv_phil")
persist_text_area("Outline the research methodology, both internal and external, and the tools or platforms used in the process.", "research")

# Key Staff
st.markdown("##### Key Staff")
persist_number_input("Number of key staff members", "n_staff", min_value=0, step=1)
for i in range(st.session_state.n_staff):
    cols = st.columns([2, 2, 1, 3])
    with cols[0]: 
        persist_text_input("Name", f"staff_name_{i}", label_visibility="collapsed", placeholder=f"Staff Member #{i+1} Name")
    with cols[1]: 
        persist_text_input("Role", f"staff_role_{i}", label_visibility="collapsed", placeholder="Role")
    with cols[2]: 
        persist_number_input("Years Exp.", f"staff_years_{i}", min_value=0, label_visibility="collapsed")
    with cols[3]: 
        persist_text_input("Qualification(s)", f"staff_qual_{i}", label_visibility="collapsed", placeholder="Qualification(s)")

# Investment Committee
st.markdown("##### Investment Committee")
persist_number_input("Number of investment committee members", "n_ic", min_value=0, step=1)
for i in range(st.session_state.n_ic):
    cols = st.columns([3, 1, 4])
    with cols[0]: 
        persist_text_input("Name", f"ic_name_{i}", label_visibility="collapsed", placeholder=f"Committee Member #{i+1} Name")
    with cols[1]: 
        persist_number_input("Years Exp.", f"ic_years_{i}", min_value=0, label_visibility="collapsed")
    with cols[2]: 
        persist_text_input("Qualification(s)", f"ic_qual_{i}", label_visibility="collapsed", placeholder="Qualification(s)")

# Compliance & Governance
st.markdown("##### Compliance & Governance")
persist_text_area("Please describe the compliance process followed and controls utilised as part of your investment process.", "compliance_proc")
persist_text_area("Are there any present, past, or pending regulatory sanctions, data breaches, regulatory fines, investigations, proceedings, or matters that you would like to bring to our attention?", "regulatory_matters")
persist_text_area("Do you think we missed anything? Please add your notes or comments here.", "final_notes")

# Supporting Document Uploads
st.markdown("##### Supporting Document Uploads")
persist_file_uploader("Proof of PI Cover", "pi_cover")
persist_file_uploader("Complaints register", "complaints_reg")
persist_file_uploader("FSP Risk Registers", "risk_reg")
persist_file_uploader("Annexure Six liquidity calculation", "annexure_six") 