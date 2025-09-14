# app/main.py
"""
Smart Instrument Finder - Main Search Page
Advanced instrument search with fuzzy matching and professional UI.
"""

import streamlit as st
import json
import pandas as pd
import sys
import logging
from pathlib import Path
import base64

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('search_debug.log')
    ]
)
logger = logging.getLogger(__name__)

from app.search.fuzzy_matcher import InstrumentFuzzyMatcher
from app.search.wallet_filter import WalletFilterEngine
from app.components.search_interface import SearchInterface, render_search_tips
from app.components.result_display import ResultDisplayComponent, render_selection_summary
from app.components.wallet_selector import WalletSelectorComponent, render_user_info_section, render_search_stats
from app.components.selection_panel import SelectionPanel
from app.components.sidebar import render_sidebar
from app.services.selection_manager import SelectionManager
from app.utils import initialize_state, add_to_search_history, load_instruments_data
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS, ONBOARDING_SECTION_CSS, SIDEBAR_GRADIENT_CSS, SIDEBAR_FINAL_ENFORCEMENT_CSS

# --- Page Config & Setup ---
st.set_page_config(
    page_title="Find Instruments",
    page_icon=str(Path(__file__).parent.parent / "assets" / "logos" / "favicon.svg"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# Page naming and navigation styling now handled by SIDEBAR_GRADIENT_CSS

st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)
st.markdown(ONBOARDING_SECTION_CSS, unsafe_allow_html=True)
st.markdown(SIDEBAR_GRADIENT_CSS, unsafe_allow_html=True)
st.markdown(SIDEBAR_FINAL_ENFORCEMENT_CSS, unsafe_allow_html=True)
initialize_state()

# --- Data Loading & Caching ---
@st.cache_data
def load_application_data():
    """Load all application data with caching for performance."""
    logger.info("Starting application data loading...")
    
    # Check for the actual CSV file path
    possible_paths = [
        Path(__file__).parent.parent / "data" / "Instrument_data.csv",
        Path(__file__).parent / "data" / "Instrument_Data_Format_Example.csv",
        Path(__file__).parent.parent / "data" / "Instrument_Data_Format_Example.csv"
    ]
    
    logger.info(f"Checking for CSV file in paths: {[str(p) for p in possible_paths]}")
    
    csv_path = None
    for path in possible_paths:
        logger.info(f"Checking path: {path} - Exists: {path.exists()}")
        if path.exists():
            csv_path = path
            logger.info(f"Found CSV file at: {csv_path}")
            break
    
    if not csv_path:
        logger.error("No CSV file found in any of the expected locations")
        st.error("Instrument data CSV file not found. Please ensure the data file is available.")
        st.stop()
    
    wallet_config_path = Path(__file__).parent / "data" / "wallet_specifications.json"
    logger.info(f"Wallet config path: {wallet_config_path} - Exists: {wallet_config_path.exists()}")
    
    # Load instruments data
    logger.info(f"Loading instruments data from: {csv_path}")
    instruments_df = load_instruments_data(str(csv_path))
    logger.info(f"Loaded {len(instruments_df)} instruments")
    
    # Load wallet configuration
    try:
        with open(wallet_config_path, 'r') as f:
            wallet_config = json.load(f)
    except Exception:
        # Fallback configuration
        wallet_config = {
            "wallet_mappings": {
                "2": {"name": "ZAR", "display_name": "EasyEquities ZAR", "currency": "ZAR", "active": True},
                "3": {"name": "TFSA", "display_name": "Tax-Free Savings Account", "currency": "ZAR", "active": True},
                "9": {"name": "RA", "display_name": "Retirement Annuity", "currency": "ZAR", "active": True},
                "10": {"name": "USD", "display_name": "EasyEquities USD", "currency": "USD", "active": True}
            },
            "default_wallets": ["ZAR", "USD", "TFSA", "RA"]
        }
    
    return instruments_df, wallet_config

def main():
    """Main function for the Smart Instrument Finder."""
    
    # Initialize core components
    try:
        instruments_df, wallet_config = load_application_data()
    except Exception as e:
        st.error(f"Failed to load application data: {e}")
        st.stop()
    
    if instruments_df.empty:
        st.error("No instrument data available. Please check the data file.")
        st.stop()
    
    wallet_filter = WalletFilterEngine(str(Path(__file__).parent / "data" / "wallet_specifications.json"))
    fuzzy_matcher = InstrumentFuzzyMatcher(instruments_df, threshold=75)
    
    # Initialize components
    search_interface = SearchInterface("e.g., 'Apple', 'AAPL', 'US0378331005'")
    result_display = ResultDisplayComponent(wallet_filter)
    wallet_selector = WalletSelectorComponent()
    selection_panel = SelectionPanel()

    # --- Render UI ---
    render_sidebar()

    # Prepare logo data URI
    logo_path = Path(__file__).parent.parent / "assets" / "logos" / "eelogowhite.svg"
    logo_data_uri = ""
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as f:
                svg_bytes = f.read()
            svg_b64 = base64.b64encode(svg_bytes).decode("utf-8")
            logo_data_uri = f"data:image/svg+xml;base64,{svg_b64}"
        except Exception:
            logo_data_uri = ""

    # Add CSS for animations and comprehensive top spacing removal
    st.markdown("""
    <style>
        /* Remove Streamlit header completely */
        .stApp > header,
        header[data-testid="stHeader"] {
            height: 0 !important;
            display: none !important;
        }
        
        /* Comprehensive top spacing removal - following working example */
        .main .block-container {
            padding-top: 0.25rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }
        
        /* Remove all top margins from first elements */
        .element-container:first-child,
        .element-container:first-child > div,
        .element-container:first-child > div > div {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* Remove top spacing from main content area */
        [data-testid="stMain"] {
            padding-top: 0 !important;
        }
        
        [data-testid="stMain"] > div {
            padding-top: 0 !important;
        }
        
        /* Remove top spacing from the main container */
        .main {
            padding-top: 0 !important;
        }
        
        /* Ensure the first element in main has no top spacing */
        .main .block-container > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* Target app view container */
        [data-testid="stAppViewContainer"] {
            padding-top: 0 !important;
        }
        
        /* Banner positioning - completely flush */
        .banner-container {
            margin-top: 0 !important;
            margin-bottom: 20px;
        }
        
        /* Sidebar styling now handled by SIDEBAR_GRADIENT_CSS from styling.py */
        
        @keyframes gradient-move {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .banner-container {
            height: 200px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            padding: 0 2rem;
        }
        
        .banner-bg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(120deg, #f4942a, #ff6b35, #e8530f, #d4410a, #f4942a);
            background-size: 300% 300%;
            animation: gradient-move 6s infinite ease-in-out;
            z-index: 0;
        }
        
        .banner-content {
            position: relative;
            z-index: 1;
            text-align: left;
            color: white !important;
            flex: 1;
        }
        
        .banner-logo {
            height: 40px;
            width: auto;
            display: block;
            margin-bottom: 8px;
        }
        
        .banner-title {
            font-size: 2.5rem;
            font-weight: 300;
            margin: 0;
            letter-spacing: 1px;
            color: white !important;
            line-height: 1.2;
        }
        
        .banner-subtitle {
            font-size: 1.1rem !important;
            margin-top: -15px !important;
            margin-bottom: 0 !important;
            color: white !important;
            font-weight: 500 !important;
        }
        
        /* Additional specific targeting for paragraph elements */
        .banner-content p {
            color: white !important;
        }
        
        .banner-container p {
            color: white !important;
        }
        
        @media (prefers-reduced-motion: reduce) {
            .banner-bg { animation: none !important; }
        }
        
        @media (max-width: 768px) {
            .banner-title { font-size: 2rem !important; }
            .banner-subtitle { font-size: 1rem !important; }
        }
    </style>
    """, unsafe_allow_html=True)

    # Animated Banner Header using CSS classes
    logo_img_html = f'<img src="{logo_data_uri}" class="banner-logo" alt="EasyEquities" />' if logo_data_uri else ""
    banner_html = f"""
    <div class="banner-container">
        <div class="banner-bg"></div>
        <div class="banner-content">
            {logo_img_html}
            <h1 class="banner-title">Share Transfer Instruction</h1>
            <p class="banner-subtitle" style="color: white !important;">Digital Securities Transfer Platform</p>
        </div>
    </div>
    """
    
    st.markdown(banner_html, unsafe_allow_html=True)

    # --- Sidebar: Navigation and Selection Panel ---
    with st.sidebar:
        # Search statistics (only show if user has started searching)
        if st.session_state.get("user_name") and st.session_state.get("user_id"):
            render_search_stats()
            
        # Persistent Selection Panel in Sidebar
        if st.session_state.get("show_selection_panel", True):
            st.markdown("---")
            selection_panel.render_persistent_panel(location="sidebar")

    # --- Main Content: User Onboarding & Search Interface ---
    
    # Getting Started Information Card (Always visible at top)
    # Use expander as a card container with custom styling
    st.markdown("""
    <style>
    /* Style the container to look like a card */
    div[data-testid="stExpander"]:has(summary:contains("Getting Started")) {
        background: linear-gradient(135deg, #fff5f0 0%, #ffffff 100%);
        border: 2px solid #f4942a;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(244, 148, 42, 0.1);
        transition: all 0.3s ease;
        margin: 20px 0;
    }
    
    div[data-testid="stExpander"]:has(summary:contains("Getting Started")):hover {
        box-shadow: 0 8px 25px rgba(244, 148, 42, 0.2);
        transform: translateY(-2px);
    }
    
    /* Hide the expander arrow and style the header */
    div[data-testid="stExpander"] summary:contains("Getting Started") {
        display: none !important;
    }
    
    /* Style for step badges */
    .step-number {
        display: inline-block;
        background: #f4942a;
        color: white;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        line-height: 28px;
        text-align: center;
        font-weight: bold;
        margin-right: 10px;
        box-shadow: 0 2px 8px rgba(244, 148, 42, 0.3);
    }
    
    .step-title {
        font-weight: 600;
        color: #333;
        margin-bottom: 4px;
    }
    
    .step-desc {
        color: #666;
        margin-left: 38px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create an expander that's always expanded and styled as a card
    with st.expander("Getting Started", expanded=True):
        
        # Step 1
        st.markdown('<span class="step-number">1</span><span class="step-title">Provide Your Information</span>', unsafe_allow_html=True)
        st.markdown('<div class="step-desc">Enter your name and EasyEquities User ID below to begin the process.</div>', unsafe_allow_html=True)
        
        # Step 2
        st.markdown('<span class="step-number">2</span><span class="step-title">Choose Your Investment Context</span>', unsafe_allow_html=True)
        st.markdown('<div class="step-desc">Select the wallet/account type for your portfolio transfer.</div>', unsafe_allow_html=True)
        
        # Step 3
        st.markdown('<span class="step-number">3</span><span class="step-title">Find Your Instruments</span>', unsafe_allow_html=True)
        st.markdown('<div class="step-desc"><b>Option A:</b> Search manually for each instrument<br><b>Option B:</b> Upload your statement via the <b>AI Assistance</b> page for automatic extraction</div>', unsafe_allow_html=True)
        
        # Step 4
        st.markdown('<span class="step-number">4</span><span class="step-title">Verify Instrument Availability</span>', unsafe_allow_html=True)
        st.markdown('<div class="step-desc">We\'ll check if your instruments are available in our EasyEquities ecosystem.</div>', unsafe_allow_html=True)
        
        # Step 5
        st.markdown('<span class="step-number">5</span><span class="step-title">Configure Portfolio Details</span>', unsafe_allow_html=True)
        st.markdown('<div class="step-desc">Edit and complete your portfolio transfer information on the <b>Portfolio</b> page.</div>', unsafe_allow_html=True)
        
        # Step 6
        st.markdown('<span class="step-number">6</span><span class="step-title">Submit Your Request</span>', unsafe_allow_html=True)
        st.markdown('<div class="step-desc">Navigate to the <b>Submit</b> page to finalize your share transfer instruction.</div>', unsafe_allow_html=True)
        
        # Warning section
        st.markdown("---")
        st.warning("""
        **⚠️ Important Notes**
        
        • **Session Data:** Your information will be lost if you close or refresh this page
        
        • **AI Verification:** Always double-check AI-extracted results as AI can occasionally make errors
        
        • **Next Steps:** After submission, the EasyEquities team will contact you with approval steps
        """)
    
    # Step 1: User Information (prominent in main area)
    user_name = st.session_state.get("user_name", "")
    user_id = st.session_state.get("user_id", "")
    
    if not user_name or not user_id:
        # User Onboarding Section
        st.markdown("Please provide your information to begin searching for instruments:")
        
        # Create a nice container for the user info
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                user_name = st.text_input(
                    "Your Name",
                    value=st.session_state.get("user_name", ""),
                    placeholder="Enter your full name",
                    help="This will be used to personalize your search experience",
                    key="user_name_input"
                )
            
            with col2:
                user_id = st.text_input(
                    "User ID", 
                    value=st.session_state.get("user_id", ""),
                    placeholder="Enter your EasyEquities user ID",
                    help="Your unique identifier for tracking and support",
                    key="user_id_input"
                )
        
        # Update session state
        if user_name:
            st.session_state.user_name = user_name
        if user_id:
            st.session_state.user_id = user_id
        
        # Progress indicator
        if user_name and user_id:
            st.success("Great! Your information has been captured.")
        elif user_name or user_id:
            st.info("Please complete both fields above to continue.")
        else:
            st.info("Please enter your name and user ID to get started.")
        
        st.markdown("---")
    
    # Step 2: Wallet Selection (only show if user info is complete)
    selected_wallet = None
    selected_wallet_id = None
    selected_wallet_info = None
    
    if user_name and user_id:
        # Wallet Selection Section
        st.markdown("## Check whether your instruments are available in EasyEquities")
        
        # Journey Selection Section with improved styling
        st.markdown("""
        <style>
        .journey-card {
            background: linear-gradient(135deg, #fff8f0 0%, #ffffff 100%);
            border: 2px solid #f4942a;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(244, 148, 42, 0.1);
            transition: all 0.3s ease;
        }
        
        .journey-card:hover {
            box-shadow: 0 8px 25px rgba(244, 148, 42, 0.2);
            transform: translateY(-2px);
        }
        
        .journey-title {
            color: #f4942a;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        
        .journey-icon {
            font-size: 1.5rem;
            margin-right: 10px;
        }
        
        .journey-description {
            color: #666;
            margin-bottom: 15px;
            line-height: 1.5;
        }
        
        .journey-benefits {
            background: rgba(244, 148, 42, 0.1);
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
        }
        
        .journey-benefits ul {
            margin: 0;
            padding-left: 20px;
        }
        
        .journey-benefits li {
            margin: 5px 0;
            color: #555;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Journey Options
        st.markdown("**Choose your preferred method to check instrument availability:**")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="journey-card">
                <div class="journey-title">
                    <span class="journey-icon">🤖</span>
                    AI-Powered Statement Upload
                </div>
                <div class="journey-description">
                    Upload your investment statement and let AI automatically extract and populate your instrument information.
                </div>
                <div class="journey-benefits">
                    <strong>Perfect for:</strong>
                    <ul>
                        <li>Multiple instruments in one statement</li>
                        <li>Complex portfolio transfers</li>
                        <li>Time-saving automation</li>
                        <li>Reducing manual entry errors</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Start with AI Assistance", type="primary", use_container_width=True):
                st.switch_page("pages/1_AI_Assistance.py")
        
        with col2:
            st.markdown("""
            <div class="journey-card">
                <div class="journey-title">
                    <span class="journey-icon">🔍</span>
                    Manual Instrument Search
                </div>
                <div class="journey-description">
                    Search for instruments one by one using the search field below to verify availability in EasyEquities.
                </div>
                <div class="journey-benefits">
                    <strong>Perfect for:</strong>
                    <ul>
                        <li>Single or few instruments</li>
                        <li>Specific instrument verification</li>
                        <li>Direct control over search process</li>
                        <li>Quick availability checks</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("👇 Continue below to use manual search")
        
        st.markdown("---")
        
        # Wallet Selection (for manual search)
        st.markdown("### Manual Search Configuration")
        st.markdown("Select your wallet context for instrument availability checking:")
        
        with st.container():
            # Add "All Wallets" as the first option
            wallet_options = [("all", {"name": "All Wallets", "display_name": "All Wallets", "currency": "Multi", "active": True})]
            
            # Then add active wallets from config
            wallet_options.extend([
                (wallet_id, info) 
                for wallet_id, info in wallet_config["wallet_mappings"].items() 
                if info.get("active", True)
            ])
            
            # Create display labels
            wallet_labels = []
            wallet_ids = []
            
            for wallet_id, info in wallet_options:
                if wallet_id == "all":
                    label = "All Wallets - Search across all available wallets"
                else:
                    currency = info.get("currency", "")
                    currency_display = f" ({currency})" if currency else ""
                    label = f"{info['name']} - {info['display_name']}{currency_display}"
                wallet_labels.append(label)
                wallet_ids.append(wallet_id)
            
            if wallet_options:
                # Default to "All Wallets" (index 0) if not previously selected
                default_index = 0
                if 'selected_wallet_id' in st.session_state and st.session_state.selected_wallet_id in wallet_ids:
                    default_index = wallet_ids.index(st.session_state.selected_wallet_id)
                
                selected_index = st.selectbox(
                    "Wallet Context:",
                    range(len(wallet_options)),
                    index=default_index,
                    format_func=lambda x: wallet_labels[x],
                    key="main_wallet_selector",
                    help="Choose 'All Wallets' to search across all available wallets, or select a specific wallet to filter results"
                )
                
                selected_wallet_id = wallet_ids[selected_index]
                selected_wallet_info = wallet_options[selected_index][1]
                selected_wallet = selected_wallet_info["name"]
                
                # Store in session state
                st.session_state.selected_wallet = selected_wallet
                st.session_state.selected_wallet_id = selected_wallet_id
                
                # Show wallet info in an expandable section
                if selected_wallet_id == "all":
                    with st.expander("About All Wallets Search", expanded=False):
                        st.info("""
                        **All Wallets** searches across the entire instrument database without wallet restrictions.
                        
                        This is ideal when:
                        - You're not sure which wallet contains your instruments
                        - You want to see all available options
                        - You're importing from a PDF statement with mixed instruments
                        
                        Results will show which wallets each instrument is available in.
                        """)
                else:
                    with st.expander(f"About {selected_wallet_info.get('display_name', 'This Wallet')}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Currency:** {selected_wallet_info.get('currency', 'N/A')}")
                            st.write(f"**Wallet Type:** {selected_wallet_info.get('name', 'N/A')}")
                        with col2:
                            st.write(f"**Status:** Active")
                            st.write(f"**ID:** {selected_wallet_id}")
        
        st.markdown("---")

    # Step 3: Search Interface (only show if user info and wallet are complete)
    if user_name and user_id and selected_wallet:
        # Search Section Header - REMOVED
        # st.markdown("## Search for Instruments")
        # st.markdown(f"**Searching in:** {selected_wallet_info.get('display_name', selected_wallet)} • **User:** {user_name}")
        
        # Search Interface
        search_params = search_interface.render()
        
        # Search Tips - COMMENTED OUT
        # render_search_tips()
        
        # Perform Search
        if search_params['search_triggered'] and search_params['query'].strip():
            query = search_params['query'].strip()
            
            with st.spinner("Searching through thousands of instruments..."):
                # Update fuzzy matcher settings
                fuzzy_matcher.threshold = search_params['fuzzy_threshold']
                
                # Perform search
                search_results = fuzzy_matcher.search_instruments(
                    query, 
                    selected_wallet_id, 
                    max_results=search_params['max_results']
                )
                
                # Update session state
                st.session_state.current_results = search_results
                st.session_state.last_search_query = query  # Store for SelectionManager
                add_to_search_history(query, len(search_results), selected_wallet)
                
        
        # Display Results
        current_results = st.session_state.get("current_results", [])
        if current_results:
            # st.info(f"Displaying {len(current_results)} search results...") - COMMENTED OUT
            # Display results with selection
            result_display.render_results(current_results, allow_selection=True)
            
            # Selection summary and navigation
            render_selection_summary()
        
        elif search_params.get('query', '').strip():
            st.info("Click 'Smart Search' to find instruments")
        
        # Always show selection management panel if user has selections
        selected_instruments = SelectionManager.get_selections()
        if selected_instruments and user_name and user_id and selected_wallet:
            st.markdown("---")
            selection_panel.render_persistent_panel(location="main")

    # else:
        # Show information about the app while user completes onboarding - REMOVED
        # About Smart Instrument Finder expandable card has been removed for cleaner UI

    # --- Footer ---
    st.markdown("---")
    st.caption("Smart Instrument Finder • Powered by EasyEquities • Advanced fuzzy search technology")

if __name__ == "__main__":
    main() 