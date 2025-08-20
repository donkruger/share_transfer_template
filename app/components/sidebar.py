# app/components/sidebar.py

from pathlib import Path
import streamlit as st
from app.utils import svg_image_html

def render_sidebar():
    """Renders the sidebar with custom page navigation."""
    # CSS to hide native Streamlit page navigation
    hide_native_nav_css = """
    <style>
    /* Hide native Streamlit page navigation */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
    """
    st.markdown(hide_native_nav_css, unsafe_allow_html=True)
    
    with st.sidebar:
        # Logo at the top of sidebar
        logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "stx_svg.svg"
        if logo_path.exists():
            st.image(str(logo_path), width=240)
        
        st.markdown("---")
        
        # Custom page navigation with proper labels and icons
        # Paths must be relative to the app directory
        st.page_link('main.py', label='Capture Info')
        st.page_link('pages/1_AI_Assistance.py', label='AI Assistance', icon='🤖')
        st.page_link('pages/3_Declaration_and_Submit.py', label='Declaration & Submit') 