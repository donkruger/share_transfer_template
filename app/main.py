# app/main.py
"""
Entity Onboarding - Introduction Page
Dynamic form rendering based on entity type selection.
"""
from __future__ import annotations
import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path to allow absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import all modular components
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS
from app.components.sidebar import render_sidebar
from app.utils import initialize_state, persist_selectbox, persist_text_input, current_namespace, ns_key
from app.controlled_lists_enhanced import get_entity_types
from app.forms.engine import render_form
from app.forms.specs import SPECS

def main():
    """Main function to run the Streamlit app's home page."""
    # ──────────────────────────────────────────────────────────────────────────
    # Page config & styling - This is the ONLY place st.set_page_config should be called
    # ──────────────────────────────────────────────────────────────────────────
    favicon_path = Path(__file__).resolve().parent.parent / "assets" / "logos" / "favicon.svg"
    st.set_page_config(
        "Entity Onboarding", 
        str(favicon_path), 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
    st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
    st.markdown(FADE_IN_CSS, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────────
    # Centralized Session State Initialization
    # ──────────────────────────────────────────────────────────────────────────
    initialize_state()

    # ──────────────────────────────────────────────────────────────────────────
    # Render UI components
    # ──────────────────────────────────────────────────────────────────────────
    render_sidebar()

    st.markdown('<h1 class="gradient-title">Juristics ReFICA</h1>', unsafe_allow_html=True)
    
    # Development Mode Toggle (for testing purposes)
    with st.expander("🔧 Development Mode", expanded=False):
        st.markdown("""
        **Development Mode** allows you to bypass form validation for testing purposes.
        ⚠️ **Warning**: This should only be used for testing - it will allow submission with incomplete data.
        """)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Toggle Dev Mode", type="secondary"):
                from app.utils import toggle_dev_mode
                toggle_dev_mode()
                st.rerun()
        
        with col2:
            from app.utils import is_dev_mode
            dev_status = "🟢 **ENABLED**" if is_dev_mode() else "🔴 **DISABLED**"
            st.markdown(f"**Status**: {dev_status}")
            
            if is_dev_mode():
                st.success("✅ Development mode is active. Form validation is disabled.")
                st.info("💡 You can now test the email engine without filling all required fields.")
            else:
                st.info("ℹ️ Development mode is disabled. All form validation rules apply.")
    
    # Welcome card with instructions
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #e8f4fd 0%, #d1e9ff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #0fbce3;
        margin: 1rem 0 2rem 0;
        box-shadow: 0 2px 10px rgba(15, 188, 227, 0.1);
    ">
        <h3 style="color: #2c5aa0; margin-top: 0; margin-bottom: 1rem; font-family: 'Questrial', sans-serif;">
            Getting Started
        </h3>
        <p style="color: #2c5aa0; line-height: 1.6; margin-bottom: 1rem; font-size: 1rem;">
            <strong>Welcome to our Entity Onboarding system!</strong> Please follow these simple steps:
        </p>
        <ul style="color: #2c5aa0; line-height: 1.8; margin-bottom: 1rem; padding-left: 1.5rem;">
            <li><strong>Select your entity type</strong> from the dropdown below</li>
            <li><strong>Enter your Entity User ID</strong> for identification</li>
            <li><strong>Complete all required fields</strong> in each section (they'll expand as you click them)</li>
        </ul>
        <p style="color: #2c5aa0; line-height: 1.6; margin-bottom: 1rem; font-size: 0.95rem;">
            🤖 <strong>Need help?</strong> Visit the <strong>"AI Assistance"</strong> helper in the left sidebar - our AI agent is trained to answer commonly asked questions and guide you through the process.
        </p>
        <p style="color: #2c5aa0; line-height: 1.6; margin-bottom: 0; font-size: 0.95rem;">
            Once you've completed all fields, proceed to the <strong>"Declaration and Submit"</strong> page to accept the declaration and finalize your submission.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Entity selector
    persist_selectbox("Entity Type", "entity_type", options=get_entity_types(include_empty=False, return_codes=False))
    ns = current_namespace()

    # EntityUserID immediately after entity type
    persist_text_input("Entity User ID", "entity_user_id")

    # Render the form according to the current spec
    spec = SPECS.get(ns)
    if not spec:
        st.warning("This entity type is not yet configured.")
        return

    # Development Mode Form Indicator
    try:
        from app.utils import is_dev_mode
        if is_dev_mode():
            st.info("""
            🔧 **Development Mode Active** - Form validation is disabled for testing purposes.
            You can now test the email engine without filling all required fields.
            """)
    except ImportError:
        pass

    render_form(spec, ns)

    # Capture a display name for downstream artifacts (email/PDF)
    # Try to get the legal name from the entity details
    legal_name = st.session_state.get(ns_key(ns, "legal_name"), "")
    if legal_name:
        st.session_state["entity_display_name"] = legal_name

    st.markdown("---")
    st.page_link('pages/3_Declaration_and_Submit.py', label='Proceed to Declaration & Submit', icon='📝')

if __name__ == "__main__":
    main() 