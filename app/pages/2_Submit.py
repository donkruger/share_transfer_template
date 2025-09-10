# app/pages/2_Submit.py

import streamlit as st
import sys
from pathlib import Path

# --- PAGE CONFIG ---
favicon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "favicon.svg"
st.set_page_config(
    page_title="Submit Results - Smart Instrument Finder",
    page_icon=str(favicon_path),
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.components.sidebar import render_sidebar
from app.components.submission import handle_search_results_submission
from app.components.result_display import ResultDisplayComponent
from app.components.feedback import render_feedback_component
from app.search.wallet_filter import WalletFilterEngine
from app.services.selection_manager import SelectionManager
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS, SIDEBAR_GRADIENT_CSS
from app.utils import initialize_state

initialize_state()
st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)

# Apply sidebar gradient styling to match main page
st.markdown(SIDEBAR_GRADIENT_CSS, unsafe_allow_html=True)

# Additional comprehensive spacing removal for this page
st.markdown("""
<style>
    /* Ensure gradient title sits flush at top */
    .gradient-title {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Remove any remaining top spacing */
    .main .block-container > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

render_sidebar()

# Professional Header
st.markdown('<h1 class="gradient-title">Submit Your Search Results</h1>', unsafe_allow_html=True)
st.markdown("**Review your selected instruments and submit your findings for processing**")

# Get user information and selected instruments using SelectionManager
user_name = st.session_state.get("user_name", "")
user_id = st.session_state.get("user_id", "")
selected_wallet = st.session_state.get("selected_wallet", "")
selected_instruments = SelectionManager.get_selections()
selection_summary = SelectionManager.get_selection_summary()

# Validation checks
if not user_name or not user_id:
    st.error("❗ Missing user information. Please return to the main page and complete your details.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Return to Search", use_container_width=True):
            st.switch_page("main.py")
    with col2:
        if st.button("Get AI Help", use_container_width=True):
            st.switch_page("pages/1_AI_Assistance.py")
    st.stop()

if not selected_instruments:
    st.warning("No instruments selected for submission.")
    st.info("Please return to the search page and select instruments to submit.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Return to Search", use_container_width=True):
            st.switch_page("main.py")
    with col2:
        if st.button("Get AI Help", use_container_width=True):
            st.switch_page("pages/1_AI_Assistance.py")
    st.stop()

# Display user and context information with enhanced summary
st.markdown("### Submission Details")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.info(f"**User:** {user_name}")
with col2:
    st.info(f"**User ID:** {user_id}")
with col3:
    st.info(f"**Wallet Context:** {selected_wallet}")
with col4:
    st.info(f"**Instruments:** {len(selected_instruments)}")

# Enhanced selection summary
if selection_summary['total_count'] > 0:
    st.markdown("### Portfolio Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Instruments", selection_summary['total_count'])
    with col2:
        st.metric("Unique Exchanges", len(selection_summary['unique_exchanges']))
    with col3:
        st.metric("Asset Types", len(selection_summary['unique_asset_types']))
    with col4:
        if selection_summary.get('oldest_selection'):
            oldest = selection_summary['oldest_selection'][:10]  # Date only
            st.metric("Selection Period", f"Since {oldest}")

# Display selected instruments for review
st.markdown(f"### Selected Instruments ({len(selected_instruments)})")

# Initialize wallet filter for display
wallet_filter = WalletFilterEngine(str(Path(__file__).parent.parent / "data" / "wallet_specifications.json"))
result_display = ResultDisplayComponent(wallet_filter)

# Display selected instruments (read-only)
with st.container():
    st.markdown("**Review your selected instruments below:**")
    
    for idx, instrument in enumerate(selected_instruments):
        # Get selection metadata
        metadata = SelectionManager.get_selection_metadata(instrument)
        
        # Enhanced expander title with selection info
        expander_title = f"{instrument.get('name', 'Unknown Instrument')}"
        if metadata.get('selected_at'):
            selected_date = metadata['selected_at'][:10]  # Date only
            expander_title += f" (Selected: {selected_date})"
        
        with st.expander(expander_title, expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Name:** {instrument.get('name', 'N/A')}")
                st.write(f"**Ticker:** {instrument.get('ticker', 'N/A')}")
                st.write(f"**ISIN:** {instrument.get('isin', 'N/A')}")
                st.write(f"**Asset Type:** {instrument.get('asset_type', 'N/A')}")
            
            with col2:
                st.write(f"**Exchange:** {instrument.get('exchange', 'N/A')}")
                st.write(f"**Currency:** {instrument.get('currency', 'N/A')}")
                st.write(f"**Relevance Score:** {instrument.get('relevance_score', 0)}%")
                st.write(f"**Match Type:** {instrument.get('match_type', 'N/A').replace('_', ' ').title()}")
            
            with col3:
                # Selection metadata
                st.markdown("**Selection Info:**")
                if metadata.get('selected_at'):
                    selected_time = metadata['selected_at'][:19].replace('T', ' ')
                    st.caption(f"Selected: {selected_time}")
                if metadata.get('source_query'):
                    st.caption(f"From search: '{metadata['source_query']}'")
                
                # Remove option
                if st.button(f"Remove from Selection", key=f"remove_submit_{idx}", type="secondary"):
                    SelectionManager.remove_instrument(instrument)
                    st.success(f"Removed {instrument.get('name', 'Unknown')} from selection")
                    st.rerun()
            
            # Show wallet availability
            available_wallets = wallet_filter.get_available_wallets(
                instrument.get('account_filters', '')
            )
            if available_wallets:
                wallet_names = [w['name'] for w in available_wallets]
                st.success(f"Available in wallets: {', '.join(wallet_names)}")
            else:
                st.warning("Wallet availability information not available")

# Option to modify selection
st.markdown("### Modify Selection")
col1, col2 = st.columns(2)
with col1:
    if st.button("Return to Search & Modify", use_container_width=True):
        st.switch_page("main.py")
with col2:
    if st.button("Get AI Assistance", use_container_width=True):
        st.switch_page("pages/1_AI_Assistance.py")

st.markdown("---")

# Submission notes
st.markdown("### Additional Notes (Optional)")
submission_notes = st.text_area(
    "Add any additional notes or context for your submission:",
    placeholder="e.g., 'Looking to diversify my portfolio with these instruments', 'Need information about minimum investment amounts', etc.",
    height=100,
    key="submission_notes"
)

# Feedback component
st.markdown("### Feedback (Optional)")
feedback_data = render_feedback_component()
if feedback_data:
    st.session_state['feedback_data'] = feedback_data

# Declaration and submission
st.markdown("---")
st.markdown("### Declaration & Submit")

# Declaration checkbox
declaration_accepted = st.checkbox(
    "I declare that the information provided is accurate and I understand that this submission is for informational purposes to help me find available instruments in the EasyEquities ecosystem.",
    key="declaration_accepted"
)

if declaration_accepted:
    st.success("Declaration accepted")
else:
    st.info("Please accept the declaration to proceed with submission")

# Submission summary
st.markdown("#### Submission Summary")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Selected Instruments", len(selected_instruments))
with col2:
    exact_matches = sum(1 for inst in selected_instruments if inst.get('match_type', '').startswith('exact'))
    st.metric("Exact Matches", exact_matches)
with col3:
    avg_relevance = sum(inst.get('relevance_score', 0) for inst in selected_instruments) / len(selected_instruments)
    st.metric("Avg. Relevance", f"{avg_relevance:.1f}%")

# Final submission button
if st.button("Submit Search Results", 
            type="primary", 
            use_container_width=True,
            disabled=not declaration_accepted):
    
    if not declaration_accepted:
        st.error("Please accept the declaration before submitting.")
        st.stop()

    # Prepare user info
    user_info = {
        "user_name": user_name,
        "user_id": user_id,
        "selected_wallet": selected_wallet,
        "declaration_accepted": declaration_accepted
    }
    
    # Handle the submission
    try:
        handle_search_results_submission(
            selected_instruments=selected_instruments,
            user_info=user_info,
            submission_notes=submission_notes
        )
        
        # Clear the selected instruments after successful submission using SelectionManager
        SelectionManager.clear_selections(confirm=True)
        
        # Success actions
        st.markdown("### Submission Successful!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start New Search", use_container_width=True):
                # Clear search state for new search (selections already cleared above)
                st.session_state.current_results = []
                st.switch_page("main.py")
        
        with col2:
            if st.button("Get More AI Help", use_container_width=True):
                st.switch_page("pages/1_AI_Assistance.py")
        
        st.balloons()
        
    except Exception as e:
        st.error(f"Submission failed: {e}")
        st.error("Please try again or contact support if the problem persists.")

# Help section
with st.expander("What happens after submission?", expanded=False):
    st.markdown("""
    **After you submit your search results:**
    
    1. **Email Confirmation**: You'll receive an email with your search results and selected instruments
    
    2. **PDF Report**: A comprehensive PDF report will be generated with all your selections
    
    3. **CSV Data**: Raw data in CSV format for your own analysis
    
    4. **Next Steps**: The EasyEquities team will review your submission and may contact you with:
       - Availability confirmation for your selected instruments
       - Information about minimum investment amounts
       - Account setup assistance if needed
       - Alternative instrument suggestions
    
    **Note**: This is an informational service to help you discover available instruments. 
    It does not constitute financial advice or create any trading obligations.
    """)

# Footer
st.markdown("---")
st.caption("Smart Instrument Finder • Submit Results • Your search journey ends here, your investment journey begins!")

# Show submission history if available
search_history = st.session_state.get("search_history", [])
if search_history:
    with st.expander("Your Search History", expanded=False):
        st.markdown("**Recent searches in this session:**")
        for search in reversed(search_history[-5:]):  # Show last 5 searches in reverse order
            timestamp = search.get('timestamp', 'Unknown time')
            query = search.get('query', 'Unknown query')
            results_count = search.get('results_count', 0)
            wallet = search.get('wallet', 'Unknown wallet')
            
            st.caption(f"{timestamp.split('T')[1][:5]} | '{query}' → {results_count} results in {wallet} wallet")