# app/components/submission.py

import datetime
import json
from typing import Dict, List, Any, Optional
import streamlit as st
from app.pdf_generator import make_pdf
from app.email_sender import send_submission_email

def handle_search_results_submission(selected_instruments: List[Dict], user_info: Dict[str, str], submission_notes: str = ""):
    """Handles the search results submission, generating PDF, sending email, and showing download options."""
    
    if not selected_instruments:
        st.error("❗ No instruments selected for submission.")
        st.stop()
    
    if not user_info.get("user_name") or not user_info.get("user_id"):
        st.error("❗ User name and ID are required for submission.")
        st.stop()

    # Show a spinner while processing
    with st.spinner("Processing search results submission..."):
        user_name = user_info.get("user_name", "Unknown User")
        dt = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        safe_user_name = user_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        pdf_name = f"Instrument_Search_Results_{safe_user_name}_{dt}.pdf"

        # Prepare submission data
        submission_data = {
            "user_info": user_info,
            "search_context": {
                "wallet": st.session_state.get("selected_wallet", "Unknown"),
                "wallet_id": st.session_state.get("selected_wallet_id", ""),
                "search_history": st.session_state.get("search_history", [])
            },
            "selected_instruments": selected_instruments,
            "submission_notes": submission_notes,
            "submission_timestamp": datetime.datetime.now().isoformat()
        }

        # 1. Send the email with search results
        try:
            send_search_results_email(submission_data)
        except Exception as e:
            st.error(f"Email sending failed: {e}")
            # Continue with PDF generation even if email fails

        # 2. Generate PDF for download
        try:
            pdf_bytes = make_search_results_pdf(submission_data)
        except Exception as e:
            st.error(f"PDF generation failed: {e}")
            st.error(f"Submission data: {str(submission_data)[:500]}")
            pdf_bytes = None

    # Success message with balloons
    st.success(f"Search results submission for **{user_name}** processed successfully!")
    st.balloons()

    # Download section
    if pdf_bytes:
        st.markdown("### Download Your Results")
        st.download_button(
            label="Download Search Results Summary (PDF)",
            data=pdf_bytes,
            file_name=pdf_name,
            mime="application/pdf",
            use_container_width=True
        )

    # Generate CSV download
    csv_data = generate_instruments_csv(selected_instruments)
    if csv_data:
        csv_name = f"Instrument_Search_Results_{safe_user_name}_{dt}.csv"
        st.download_button(
            label="Download Results as CSV",
            data=csv_data,
            file_name=csv_name,
            mime="text/csv",
            use_container_width=True
        )

    # Raw JSON data (collapsed by default)
    with st.expander("Show raw submission data"):
        st.json(submission_data, expanded=False)


def send_search_results_email(submission_data: Dict[str, Any]):
    """Send search results via email."""
    # This will use the existing email infrastructure
    # For now, we'll use the existing send_submission_email function
    send_submission_email(submission_data, [])


def make_search_results_pdf(submission_data: Dict[str, Any]) -> bytes:
    """Generate PDF for search results."""
    # This will use the existing PDF infrastructure
    # For now, we'll use the existing make_pdf function
    return make_pdf(submission_data)


def generate_instruments_csv(instruments: List[Dict]) -> str:
    """Generate CSV content from selected instruments."""
    if not instruments:
        return ""
    
    import csv
    import io
    
    output = io.StringIO()
    
    # Get all possible field names
    fieldnames = set()
    for instrument in instruments:
        fieldnames.update(instrument.keys())
    
    fieldnames = sorted(list(fieldnames))
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for instrument in instruments:
        # Clean the data for CSV
        clean_instrument = {}
        for key, value in instrument.items():
            if isinstance(value, dict):
                # Convert dict to string representation
                clean_instrument[key] = str(value)
            else:
                clean_instrument[key] = value
        writer.writerow(clean_instrument)
    
    return output.getvalue()


# Keep the original function for backward compatibility
def handle_submission(answers: Dict[str, Any], uploaded_files: List[Optional[st.runtime.uploaded_file_manager.UploadedFile]]):
    """Legacy submission handler - kept for backward compatibility."""
    # This is the original function, kept in case any legacy code still references it
    send_submission_email(answers, uploaded_files)