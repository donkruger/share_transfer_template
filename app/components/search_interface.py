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
        # st.markdown("### Intelligent Instrument Search") - REMOVED
        
        # Add unique CSS for ONLY this search input with enhanced icon positioning
        st.markdown(f"""
        <style>
        /* Create a container for the search input with icon */
        .main-search-input-{key_prefix} {{
            position: relative;
            display: block;
        }}
        
        /* Target ONLY the main search input by its unique key */
        .main-search-input-{key_prefix} input,
        .main-search-input-{key_prefix} div[data-testid="stTextInput"] input {{
            padding-left: 20px !important;
            padding-right: 50px !important;
            border-radius: 50px !important;
            border: 2px solid #e0e0e0 !important;
            font-size: 16px !important;
            height: 48px !important;
            transition: all 0.3s ease !important;
            background-color: #ffffff !important;
            box-shadow: none !important;
        }}
        
        .main-search-input-{key_prefix} input:focus,
        .main-search-input-{key_prefix} div[data-testid="stTextInput"] input:focus {{
            border-color: #f4942a !important;
            box-shadow: 0 0 0 3px rgba(244, 148, 42, 0.15) !important;
            outline: none !important;
        }}
        
        .main-search-input-{key_prefix} input:hover,
        .main-search-input-{key_prefix} div[data-testid="stTextInput"] input:hover {{
            border-color: #ccc !important;
        }}
        
        /* Remove background from wrapper elements for this specific input */
        .main-search-input-{key_prefix} > div[data-testid="stTextInput"] > div,
        .main-search-input-{key_prefix} > div[data-testid="stTextInput"] > div > div {{
            background: none !important;
            border: none !important;
            box-shadow: none !important;
            border-radius: 50px !important;
        }}
        
        /* Add search icon as an overlay element */
        .main-search-input-{key_prefix}::after {{
            content: "";
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%23666666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cpath d='m21 21-4.35-4.35'%3E%3C/path%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: center;
            background-size: 20px 20px;
            pointer-events: none;
            z-index: 10;
        }}
        
        /* Change icon color when input is focused */
        .main-search-input-{key_prefix}:focus-within::after {{
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%23f4942a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cpath d='m21 21-4.35-4.35'%3E%3C/path%3E%3C/svg%3E");
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Wrap the search input in a container with unique class
        st.markdown(f'<div class="main-search-input-{key_prefix}">', unsafe_allow_html=True)
        
        # Simplified search input - no form, triggers on change
        search_query = st.text_input(
            "Search by instrument name, ticker, or ISIN",
            key=f"{key_prefix}_input",
            placeholder=self.placeholder_text,
            help="Enter any part of the instrument name, ticker symbol, or ISIN code"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add CSS for button styling
        st.markdown("""
        <style>
        /* Style the search and clear buttons */
        .search-buttons-container {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        /* Make search button primary (orange) */
        div[data-testid="stButton"] button[kind="primary"] {
            background-color: #f4942a !important;
            border-color: #f4942a !important;
            color: white !important;
        }
        
        div[data-testid="stButton"] button[kind="primary"]:hover {
            background-color: #e8530f !important;
            border-color: #e8530f !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Search and Clear buttons in columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            search_button = st.button(
                "Search", 
                type="primary",
                key=f"{key_prefix}_search_btn",
                help="Search for instruments matching your query",
                use_container_width=True
            )
        
        with col2:
            clear_button = st.button(
                "Clear Results", 
                on_click=self._clear_results,
                key=f"{key_prefix}_clear_btn", 
                help="Clear current search results only",
                use_container_width=True
            )
        
        # Advanced search options - COMMENTED OUT
        # with st.expander("Search Options", expanded=False):
        #     col1, col2, col3 = st.columns(3)
        #     with col1:
        #         fuzzy_threshold = st.slider(
        #             "Fuzzy Match Threshold", 
        #             60, 100, 80, 5,
        #             key=f"{key_prefix}_threshold",
        #             help="Lower values return more results but may be less relevant"
        #         )
        #     with col2:
        #         max_results = st.slider(
        #             "Maximum Results", 
        #             10, 100, 50, 10,
        #             key=f"{key_prefix}_max_results",
        #             help="Limit the number of search results"
        #         )
        #     with col3:
        #         search_mode = st.selectbox(
        #             "Search Mode", 
        #             ["Smart (Recommended)", "Exact Only", "Fuzzy Only"],
        #             key=f"{key_prefix}_mode",
        #             help="Choose search strategy"
        #         )
        
        # Default values for commented out options
        fuzzy_threshold = 80
        max_results = 50
        search_mode = "Smart (Recommended)"
        
        search_params = {
            'query': search_query,
            'search_triggered': bool((search_query and search_query.strip()) or search_button),  # Trigger search when there's input OR search button clicked
            'search_button_clicked': search_button,
            'clear_triggered': clear_button,
            'fuzzy_threshold': fuzzy_threshold,
            'max_results': max_results,
            'search_mode': search_mode
        }
        
        logger.info(f"SearchInterface.render() returning: {search_params}")
        
        return search_params
    
    def _clear_results(self):
        """Clear search results and reset search input."""
        # Clear search results
        if 'current_results' in st.session_state:
            st.session_state.current_results = []
        
        # Clear the search input field by resetting its session state key
        search_input_keys = [key for key in st.session_state.keys() if key.endswith('_input')]
        for key in search_input_keys:
            if 'search' in key:  # Only clear search-related inputs
                st.session_state[key] = ""
        
        # Clear last search query
        if 'last_search_query' in st.session_state:
            st.session_state.last_search_query = ""
            
        # DO NOT clear selected_instruments - selections persist across searches

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
