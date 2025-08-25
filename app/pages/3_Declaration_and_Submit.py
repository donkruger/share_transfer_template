import streamlit as st
import sys
from pathlib import Path

# --- PAGE CONFIG ---
favicon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "favicon.svg"
st.set_page_config(
    page_title="Declaration & Submit - Entity Onboarding",
    page_icon=str(favicon_path),
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.components.sidebar import render_sidebar
from app.components.submission import handle_submission
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS
from app.utils import initialize_state, persist_checkbox, persist_text_input, current_namespace
from app.forms.specs import SPECS
from app.forms.engine import serialize_answers, validate

initialize_state()
st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)
render_sidebar()

# Add logo above title - full width landscape
logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "Ownthemarket.png"
if logo_path.exists():
    # Display logo across full width for landscape/wide format
    try:
        # Try new parameter for newer Streamlit versions
        st.image(str(logo_path), 
                use_container_width=True,
                output_format="PNG")
    except TypeError:
        # Fallback to deprecated parameter for older versions
        st.image(str(logo_path), 
                use_column_width=True,
                output_format="PNG")
else:
    st.warning("Logo not found at expected path")

st.markdown('<h1 class="gradient-title">Declaration & Submit</h1>', unsafe_allow_html=True)

# Development Mode Indicator
try:
    from app.utils import is_dev_mode
    if is_dev_mode():
        st.warning("""
        ⚠️ **DEVELOPMENT MODE ACTIVE** ⚠️
        
        Form validation is disabled. You can submit with incomplete data for testing purposes.
        This should only be used for development/testing - not for production submissions.
        """)
except ImportError:
    pass

persist_checkbox("I/we declare the information provided is true, accurate, complete, and up-to-date.", "accept")
st.markdown(" ")
cols = st.columns(2)
with cols[0]:
    persist_text_input("Signatory #1 – Full Name", "s1_name")
with cols[1]:
    persist_text_input("Signatory #1 – Designation", "s1_desig")
cols = st.columns(2)
with cols[0]:
    persist_text_input("Signatory #2 – Full Name (optional)", "s2_name")
with cols[1]:
    persist_text_input("Signatory #2 – Designation (optional)", "s2_desig")

st.markdown("---")
st.subheader("Final Submission")

def reconstruct_payload():
    ns = current_namespace()
    spec = SPECS.get(ns)
    if not spec:
        st.error("The selected entity type is not configured.")
        st.stop()

    # Formal validation pass (component + required fields)
    errors = validate(spec, ns)
    if errors:
        st.error("Please resolve the following issues before submitting:")
        for e in errors:
            st.markdown(f"- {e}")
        st.stop()

    # Use enhanced serialization when available
    attachment_collector = None
    try:
        from app.forms.engine import serialize_answers_with_metadata
        answers, attachment_collector = serialize_answers_with_metadata(spec, ns)
        
        # Get legacy upload list for backward compatibility
        uploads = attachment_collector.get_legacy_upload_list()
        
        # Debug information for development mode
        try:
            from app.utils import is_dev_mode
            if is_dev_mode():
                st.info(f"🔧 **Enhanced Serialization Active** - {attachment_collector.get_attachment_count()} attachments with metadata")
                summary = attachment_collector.get_attachment_summary()
                if summary:
                    st.info("📎 **Enhanced Attachment Names Preview:**")
                    for filename in summary[:3]:  # Show first 3
                        st.info(f"  • {filename}")
                    if len(summary) > 3:
                        st.info(f"  • ... and {len(summary) - 3} more")
        except ImportError:
            pass
        
    except ImportError:
        # Fallback to traditional serialization
        from app.forms.engine import serialize_answers
        answers, uploads = serialize_answers(spec, ns)
        st.info("ℹ️ Using legacy serialization (enhanced naming not available)")
    
    # Attach global submission metadata
    answers["Entity User ID"] = st.session_state.get("entity_user_id", "")
    answers["Declaration"] = {
        "Declaration Accepted": st.session_state.get("accept", False),
        "Signatory 1 Name": st.session_state.get("s1_name", ""),
        "Signatory 1 Designation": st.session_state.get("s1_desig", ""),
        "Signatory 2 Name": st.session_state.get("s2_name", ""),
        "Signatory 2 Designation": st.session_state.get("s2_desig", ""),
    }
    return answers, uploads, attachment_collector

if st.button("Confirm & Submit", use_container_width=True, type="primary"):
    answers_data, uploaded_files_data, attachment_collector = reconstruct_payload()
    
    # Store attachment collector in session state for submission handler
    if attachment_collector:
        st.session_state['_attachment_collector'] = attachment_collector
    
    handle_submission(answers_data, uploaded_files_data) 