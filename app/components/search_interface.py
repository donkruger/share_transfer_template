# app/components/search_interface.py

import streamlit as st
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SearchInterface:
    """
    Advanced search input component with configurable options
    and intelligent search suggestions.
    """
    
    def __init__(self, placeholder_text: str = "Search instruments..."):
        self.placeholder_text = placeholder_text
    
    def render(self, key_prefix: str = "search") -> Dict[str, Any]:
        """
        Render the search interface and return search parameters.
        """
        st.markdown("### Intelligent Instrument Search")
        
        # Use form to enable Enter key functionality
        with st.form(key=f"{key_prefix}_form"):
            # Main search input
            col1, col2 = st.columns([3, 1])
            
            with col1:
                search_query = st.text_input(
                    "Search by instrument name, ticker, or ISIN",
                    key=f"{key_prefix}_input",
                    placeholder=self.placeholder_text,
                    help="Enter any part of the instrument name, ticker symbol, or ISIN code (Press Enter to search)"
                )
            
            with col2:
                search_button = st.form_submit_button("Smart Search", type="primary", use_container_width=True)
        
        # Clear button outside the form so it doesn't interfere with Enter key behavior
        clear_button = st.button("Clear Results", on_click=self._clear_results, 
                                help="Clear current search results only")
        
        # Advanced search options
        with st.expander("⚙️ Search Options", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                fuzzy_threshold = st.slider(
                    "Fuzzy Match Threshold", 
                    60, 100, 80, 5,
                    key=f"{key_prefix}_threshold",
                    help="Lower values return more results but may be less relevant"
                )
            with col2:
                max_results = st.slider(
                    "Maximum Results", 
                    10, 100, 50, 10,
                    key=f"{key_prefix}_max_results",
                    help="Limit the number of search results"
                )
            with col3:
                search_mode = st.selectbox(
                    "Search Mode", 
                    ["Smart (Recommended)", "Exact Only", "Fuzzy Only"],
                    key=f"{key_prefix}_mode",
                    help="Choose search strategy"
                )
        
        search_params = {
            'query': search_query,
            'search_triggered': search_button,  # Form submit button handles both click and Enter key
            'clear_triggered': clear_button,
            'fuzzy_threshold': fuzzy_threshold,
            'max_results': max_results,
            'search_mode': search_mode
        }
        
        logger.info(f"SearchInterface.render() returning: {search_params}")
        
        return search_params
    
    def _clear_results(self):
        """Clear ONLY search results, preserve selections."""
        if 'current_results' in st.session_state:
            st.session_state.current_results = []
        # ✅ DO NOT clear selected_instruments - selections persist across searches

def render_search_stats(results_count: int, search_query: str = "", wallet: str = ""):
    """Render search statistics and history information."""
    if results_count > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Results", results_count)
        with col2:
            if 'search_history' in st.session_state:
                st.metric("Total Searches", len(st.session_state.search_history))
        with col3:
            if wallet:
                st.metric("Wallet Context", wallet)

def render_search_tips():
    """Render helpful search tips for users."""
    with st.expander("Search Tips", expanded=False):
        st.markdown("""
        **For best results:**
        - **Full names work best**: "Apple Inc" instead of "Apple"
        - **Use ticker symbols**: "AAPL", "MSFT", "GOOGL"
        - **ISIN codes are precise**: "US0378331005" for Apple Inc
        - **Partial matches**: "Apple" will find "Apple Inc", "Apple Computer", etc.
        
        **Search Features:**
        - **Fuzzy matching**: Finds similar spellings and variations
        - **Multi-field search**: Searches names, tickers, and ISINs simultaneously
        - **Wallet filtering**: Shows only instruments available in your selected wallet
        - **Relevance ranking**: Best matches appear first
        """)
