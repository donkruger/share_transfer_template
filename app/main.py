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
from app.utils import initialize_state, persist_selectbox, persist_text_input, current_namespace, ns_key, ENTITY_TYPES
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

    st.markdown('<h1 class="gradient-title">Entity Onboarding | Re-FICA</h1>', unsafe_allow_html=True)
    st.caption("Select an entity type. All information is captured on this page with built-in validation.")

    # Entity selector
    persist_selectbox("Entity Type", "entity_type", options=ENTITY_TYPES)
    ns = current_namespace()

    # EntityUserID immediately after entity type
    persist_text_input("Entity User ID", "entity_user_id")

    # Render the form according to the current spec
    spec = SPECS.get(ns)
    if not spec:
        st.warning("This entity type is not yet configured.")
        return

    render_form(spec, ns)

    # Capture a display name for downstream artifacts (email/PDF)
    entity_name = st.session_state.get(ns_key(ns, "entity_name"), "")
    if entity_name:
        st.session_state["entity_display_name"] = entity_name

    st.markdown("---")
    st.page_link('pages/3_Declaration_and_Submit.py', label='Proceed to Declaration & Submit', icon='📝')

if __name__ == "__main__":
    main() 