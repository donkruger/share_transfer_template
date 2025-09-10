# app/components/sidebar.py

from pathlib import Path
import streamlit as st
from app.utils import svg_image_html

def render_sidebar():
    """Renders the sidebar with custom page navigation."""
    # CSS to hide native Streamlit page navigation - COMMENTED OUT to show pages
    # hide_native_nav_css = """
    # <style>
    # /* Hide native Streamlit page navigation */
    # [data-testid="stSidebarNav"] {
    #     display: none !important;
    # }
    # </style>
    # """
    # st.markdown(hide_native_nav_css, unsafe_allow_html=True)
    
    # Get logo for CSS embedding
    logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "eesvg.svg"
    logo_data_uri = ""
    if logo_path.exists():
        try:
            import base64
            with open(logo_path, "rb") as f:
                svg_bytes = f.read()
            svg_b64 = base64.b64encode(svg_bytes).decode("utf-8")
            logo_data_uri = f"data:image/svg+xml;base64,{svg_b64}"
        except Exception:
            logo_data_uri = ""

    # Sidebar styling with logo positioning
    sidebar_css = f"""
    <style>
    /* Sidebar background styling - removed to allow gradient from main.py */
    /* Background is now handled by animated gradient in main.py */
    
    /* Reorder sidebar content: logo first, then navigation */
    [data-testid="stSidebar"] > div > div:first-child {{
        display: flex !important;
        flex-direction: column !important;
    }}
    
    /* Move navigation below logo by changing order */
    [data-testid="stSidebarNav"] {{
        order: 2 !important;
        margin-top: 0px !important;
    }}
    
    /* Add logo before navigation */
    [data-testid="stSidebarNav"]::before {{
        content: "";
        display: block;
        background-image: url('{logo_data_uri}');
        background-size: 180px auto;
        background-repeat: no-repeat;
        background-position: center;
        height: 60px;
        width: 100%;
        margin: 20px 0 15px 0;
        order: 1 !important;
    }}
    
    /* Ensure other sidebar content comes after navigation */
    [data-testid="stSidebar"] .block-container {{
        order: 3 !important;
    }}
    </style>
    """
    st.markdown(sidebar_css, unsafe_allow_html=True)
    
    with st.sidebar:        
        st.markdown("---")
        
        st.info("Please populate your information on the right to get started.") 