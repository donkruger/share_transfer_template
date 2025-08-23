# app/components/submission.py

import datetime
import json
from typing import Dict, List, Any, Optional
import streamlit as st
from app.pdf_generator import make_pdf
from app.email_sender import send_submission_email # Import the new function

def handle_submission(answers: Dict[str, Any], uploaded_files: List[Optional[st.runtime.uploaded_file_manager.UploadedFile]]):
    """Handles the form submission, generating PDF, sending email, and showing download buttons."""
    
    if not st.session_state.get("accept"):
        st.error("❗ You must tick the declaration checkbox before submitting.")
        st.stop()

    # Debug information for development mode
    try:
        from app.utils import is_dev_mode
        if is_dev_mode():
            st.info("🔧 **Development Mode Active** - Debugging submission data...")
            st.json({
                "answers_type": type(answers).__name__,
                "answers_keys": list(answers.keys()) if isinstance(answers, dict) else "N/A",
                "answers_sample": str(answers)[:200] + "..." if len(str(answers)) > 200 else str(answers),
                "uploaded_files_count": len([f for f in uploaded_files if f is not None])
            })
    except ImportError:
        pass

    # Show a spinner while processing
    with st.spinner("Processing submission..."):
        # Extract entity name from display name (set in main.py from legal_name)
        entity_name = st.session_state.get("entity_display_name", "Unknown Entity")
        dt = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        safe_entity_name = entity_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        pdf_name = f"Entity_Onboarding_{safe_entity_name}_{dt}.pdf"

        # 1. Send the email with all data and attachments
        send_submission_email(answers, uploaded_files)

        # 2. Generate PDF for download
        try:
            pdf_bytes = make_pdf(answers)
        except Exception as e:
            st.error(f"❌ PDF generation failed: {e}")
            st.error(f"Answers data type: {type(answers).__name__}")
            st.error(f"Answers content: {str(answers)[:500]}")
            st.stop()

    # Success message with balloons
    st.success(f"✅ Entity Onboarding submission for **{entity_name}** captured successfully. Please download your files below.")
    st.balloons()

    # Download section
    st.markdown("### 📄 Download Your Documents")
    st.download_button(
        label="📄 Download Entity Onboarding Summary (PDF)",
        data=pdf_bytes,
        file_name=pdf_name,
        mime="application/pdf",
        use_container_width=True
    )

    st.markdown("#### All Uploaded Supporting Documents")
    valid_uploads = [f for f in uploaded_files if f is not None]
    if valid_uploads:
        for f in valid_uploads:
            st.download_button(f"📎 {f.name}", f.getvalue(), file_name=f.name, mime=f.type)
    else:
        st.info("No supporting documents were uploaded.")

    # Raw JSON data (collapsed by default)
    with st.expander("Show raw JSON answer payload"):
        st.json(json.loads(json.dumps(answers, default=str)), expanded=False)