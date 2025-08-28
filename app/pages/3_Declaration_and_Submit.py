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

# Add enhanced banner with hover effect
logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "Ownthemarket.png"
if logo_path.exists():
    # Enhanced banner with hover effect
    banner_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css?family=Questrial:400,600,700');
    
    .banner-container {{
        width: 100%;
        margin: 0 auto 2rem auto;
        max-width: 100%;
    }}
    
    .snip *,
    .snip *:before,
    .snip *:after {{
        box-sizing: border-box;
        transition: all 0.45s ease;
    }}

    .snip {{
        position: relative;
        overflow: hidden;
        width: 100%;
        max-width: 100%;
        min-height: 200px;
        font-family: 'Questrial', sans-serif;
        color: #fff;
        font-size: 16px;
        text-align: left;
        transform: translateZ(0);
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }}

    .snip:hover .snip__title,
    .snip:hover .snip__text {{
        transform: translateY(0);
        opacity: 1;
        transition-delay: 0.2s;
    }}

    .snip::before,
    .snip::after {{
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #0fbce3 0%, #2c5aa0 100%);
        opacity: 0.7;
        transition: all 0.45s ease;
    }}

    .snip::before {{
        transform: skew(30deg) translateX(-80%);
    }}

    .snip::after {{
        transform: skew(-30deg) translateX(-70%);
    }}

    .snip:hover::before {{
        transform: skew(30deg) translateX(-20%);
        transition-delay: 0.05s;
    }}

    .snip:hover::after {{
        transform: skew(-30deg) translateX(-10%);
    }}

    .snip:hover .snip__figcaption::before {{
        transform: skew(30deg) translateX(-40%);
        transition-delay: 0.15s;
    }}

    .snip:hover .snip__figcaption::after {{
        transform: skew(-30deg) translateX(-30%);
        transition-delay: 0.1s;
    }}

    .snip__image {{
        backface-visibility: hidden;
        width: 100%;
        height: 200px;
        object-fit: cover;
        vertical-align: top;
    }}

    .snip__figcaption {{
        position: absolute;
        top: 0px;
        bottom: 0px;
        left: 0px;
        right: 0px;
        z-index: 1;
        padding: 25px 40% 25px 30px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}

    .snip__figcaption::before,
    .snip__figcaption::after {{
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #0fbce3 0%, #2c5aa0 100%);
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
        content: "";
        opacity: 0.8;
        z-index: -1;
    }}

    .snip__figcaption::before {{
        transform: skew(30deg) translateX(-100%);
    }}

    .snip__figcaption::after {{
        transform: skew(-30deg) translateX(-90%);
    }}

    .snip__title,
    .snip__text {{
        margin: 0;
        opacity: 0;
        letter-spacing: 1px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }}

    .snip__title {{
        font-family: 'Questrial', sans-serif;
        font-size: 28px;
        font-weight: 700;
        line-height: 1.2em;
        text-transform: uppercase;
        margin-bottom: 10px;
        color: #ffffff;
    }}

    .snip__text {{
        font-size: 14px;
        line-height: 1.4;
        color: #f0f8ff;
        font-weight: 400;
    }}

    @media (max-width: 768px) {{
        .snip {{
            min-height: 150px;
        }}
        .snip__image {{
            height: 150px;
        }}
        .snip__title {{
            font-size: 22px;
        }}
        .snip__text {{
            font-size: 12px;
        }}
        .snip__figcaption {{
            padding: 20px 35% 20px 25px;
        }}
    }}
    </style>
    
    <div class="banner-container">
        <figure class="snip">
            <img class="snip__image" src="data:image/png;base64,{logo_path.read_bytes().hex()}" alt="Entity Onboarding Banner" />
            <figcaption class="snip__figcaption">
                <h3 class="snip__title">Congrats, you're almost there!</h3>
                <p class="snip__text">
                    Final step: Review your information, accept the declaration, and submit your entity onboarding application.
                </p>
            </figcaption>
        </figure>
    </div>
    """
    
    # Convert image to base64 for embedding
    import base64
    with open(logo_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()
    
    # Replace the hex placeholder with actual base64
    banner_html = banner_html.replace(f"data:image/png;base64,{logo_path.read_bytes().hex()}", f"data:image/png;base64,{img_base64}")
    
    st.markdown(banner_html, unsafe_allow_html=True)
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