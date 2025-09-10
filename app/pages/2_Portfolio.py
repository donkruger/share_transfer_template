# app/pages/2_Portfolio.py

import streamlit as st
import pandas as pd
from pathlib import Path
from app.services.selection_manager import SelectionManager
from app.services.portfolio_service import PortfolioService
from app.components.share_transfer_form import ShareTransferForm
from app.components.sidebar import render_sidebar
from app.styling import (
    GOOGLE_FONTS_CSS, 
    GRADIENT_TITLE_CSS, 
    FADE_IN_CSS, 
    ONBOARDING_SECTION_CSS, 
    SIDEBAR_GRADIENT_CSS, 
    SIDEBAR_FINAL_ENFORCEMENT_CSS
)
from app.utils import initialize_state

# Page configuration
st.set_page_config(
    page_title="My Portfolio | Smart Instrument Finder",
    page_icon="Portfolio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply comprehensive styling following current conventions
st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)
st.markdown(ONBOARDING_SECTION_CSS, unsafe_allow_html=True)
st.markdown(SIDEBAR_GRADIENT_CSS, unsafe_allow_html=True)
st.markdown(SIDEBAR_FINAL_ENFORCEMENT_CSS, unsafe_allow_html=True)

# Initialize state
initialize_state()
PortfolioService.initialize_portfolio_state()

# Render sidebar with logo
render_sidebar()

# Header
st.markdown('<h1 class="gradient-text">My Portfolio</h1>', unsafe_allow_html=True)
st.markdown("**Configure share transfer details for your selected instruments**")

# Get user information
user_name = st.session_state.get("user_name", "")
user_id = st.session_state.get("user_id", "")
selected_wallet = st.session_state.get("selected_wallet", "")

# Check user onboarding
if not all([user_name, user_id, selected_wallet]):
    st.warning("Please complete your information on the main page before configuring your portfolio.")
    if st.button("Go to Main Page", type="primary"):
        st.switch_page("main.py")
    st.stop()

# Get selected instruments
selected_instruments = SelectionManager.get_selections()

if not selected_instruments:
    st.info("No instruments selected yet. Please search and select instruments first.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Search Instruments", type="primary", use_container_width=True):
            st.switch_page("main.py")
    with col2:
        if st.button("Get AI Assistance", use_container_width=True):
            st.switch_page("pages/1_AI_Assistance.py")
    st.stop()

# Portfolio overview
st.markdown("### Portfolio Overview")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Selected Instruments", len(selected_instruments))

with col2:
    portfolio_entries = PortfolioService.get_all_portfolio_entries()
    completed_entries = len([k for k in portfolio_entries.keys() 
                           if str(k) in [str(inst.get('instrument_id')) for inst in selected_instruments]])
    st.metric("Configured", completed_entries)

with col3:
    completion_rate = (completed_entries / len(selected_instruments)) * 100 if selected_instruments else 0
    st.metric("Completion", f"{completion_rate:.0f}%")

# Progress indicator
progress_value = completion_rate / 100
st.progress(progress_value)

if completion_rate < 100:
    st.info(f"⏳ Complete portfolio configuration for {len(selected_instruments) - completed_entries} remaining instrument(s)")

# Share Transfer Configuration
st.markdown("---")
st.markdown("### Share Transfer Configuration")

# Create form component instance
share_transfer_form = ShareTransferForm()

# Render forms for each selected instrument
for i, instrument in enumerate(selected_instruments):
    instrument_id = str(instrument.get('instrument_id'))
    
    with st.expander(
        f"{instrument.get('name', 'Unknown Instrument')} ({instrument.get('ticker', 'N/A')})",
        expanded=(i < 3 or PortfolioService.get_portfolio_entry(instrument_id) is None)
    ):
        # Display comprehensive instrument details
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**Exchange:** {instrument.get('exchange', 'N/A')}")
            st.caption(f"Contract: {instrument.get('contract_code', 'N/A')}")
        with col2:
            st.markdown(f"**Asset Group:** {instrument.get('asset_group', 'N/A')}")
            st.caption(f"Sub-group: {instrument.get('asset_sub_group', 'N/A')}")
        with col3:
            st.markdown(f"**Currency:** {instrument.get('currency', 'N/A')}")
            st.caption(f"ISIN: {instrument.get('isin', 'N/A')}")
        with col4:
            st.markdown(f"**ID:** {instrument.get('instrument_id', 'N/A')}")
            st.caption(f"Ticker: {instrument.get('ticker', 'N/A')}")
        
        
        st.markdown("---")
        
        # Check if this instrument has AI-populated data
        portfolio_entry = PortfolioService.get_portfolio_entry(instrument_id)
        if portfolio_entry and portfolio_entry.get('data_source') in ['ai_agent', 'pdf_parser']:
            # Show AI data review component
            st.info("This instrument has AI-populated data. Please review and confirm.")
            
            # Display AI confidence and source info
            col1, col2, col3 = st.columns(3)
            with col1:
                confidence = portfolio_entry.get('ai_confidence', 0.0)
                st.metric("AI Confidence", f"{confidence:.1%}")
            with col2:
                source_doc = portfolio_entry.get('source_document', 'Unknown')
                st.caption(f"**Source:** {source_doc}")
            with col3:
                extraction_time = portfolio_entry.get('extraction_timestamp', '')
                if extraction_time:
                    st.caption(f"**Extracted:** {extraction_time[:19].replace('T', ' ')}")
            
            # Show field-level confidence if available
            ai_fields = portfolio_entry.get('ai_extracted_fields', {})
            if ai_fields:
                st.markdown("**Field Confidence Scores:**")
                field_cols = st.columns(len(ai_fields))
                for i, (field, confidence) in enumerate(ai_fields.items()):
                    with field_cols[i]:
                        color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                        st.caption(f"{color} {field}: {confidence:.1%}")
        
        # Render share transfer form for this instrument
        share_transfer_form.render_form(instrument, f"form_{instrument_id}")

# Portfolio Actions
st.markdown("---")
st.markdown("### Portfolio Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Search More", use_container_width=True):
        st.switch_page("main.py")

with col2:
    if st.button("Get AI Help", use_container_width=True):
        st.switch_page("pages/1_AI_Assistance.py")

with col3:
    is_complete = PortfolioService.is_portfolio_complete()
    if st.button(
        "Proceed to Submit", 
        type="primary" if is_complete else "secondary",
        use_container_width=True,
        disabled=not is_complete
    ):
        if is_complete:
            st.success("Portfolio configuration complete!")
            st.switch_page("pages/3_Submit.py")
        else:
            st.error("Please complete all portfolio entries before submitting")

with col4:
    if st.button("Clear Portfolio Data", 
                type="secondary", 
                use_container_width=True):
        if st.session_state.get('confirm_clear_portfolio', False):
            PortfolioService.clear_portfolio_data()
            st.session_state.confirm_clear_portfolio = False
            st.success("Portfolio data cleared!")
            st.rerun()
        else:
            st.session_state.confirm_clear_portfolio = True
            st.warning("Click again to confirm clearing all portfolio data")

# NEW: AI Data Import Section
st.markdown("---")
st.markdown("### AI Data Import")

with st.expander("Import from AI Agent", expanded=False):
    st.markdown("""
    **For Future Integration:** This section will support importing portfolio data 
    from external AI agents that parse PDF statements.
    
    **JSON Format Expected:**
    - Structured portfolio data with confidence scores
    - Instrument identification via ticker, ISIN, or name
    - Field-level confidence metadata for user review
    """)
    
    # Placeholder for future AI import functionality
    uploaded_json = st.file_uploader(
        "Upload AI-Generated Portfolio JSON",
        type=['json'],
        help="Upload JSON file from AI agent (PDF statement parser)",
        disabled=True  # Disabled until AI integration is implemented
    )
    
    if uploaded_json:
        st.info("🚧 AI import functionality will be implemented in future release")
        # Future implementation:
        # json_data = json.load(uploaded_json)
        # result = PortfolioService.import_ai_portfolio_data(json_data)
        # Display import results and review interface

# Reset confirmation state
if 'confirm_clear_portfolio' in st.session_state and st.session_state.confirm_clear_portfolio:
    if st.button("Cancel Clear", key="cancel_clear_portfolio"):
        st.session_state.confirm_clear_portfolio = False
        st.rerun()

# Footer with helpful information
st.markdown("---")
st.caption("**Tips:** All fields are required. Use the AI Assistant if you need help with broker IDs or settlement dates.")

# Display completion status
if PortfolioService.is_portfolio_complete():
    st.success("Portfolio configuration is complete! You can now proceed to submit your results.")
else:
    remaining = len(selected_instruments) - len([k for k in portfolio_entries.keys() 
                                                if str(k) in [str(inst.get('instrument_id')) for inst in selected_instruments]])
    st.warning(f"Please complete configuration for {remaining} remaining instrument(s) before submission.")
