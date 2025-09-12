# app/components/submission.py

import datetime
import json
from typing import Dict, List, Any, Optional
import streamlit as st
from app.pdf_generator import make_pdf
from app.email_sender import send_submission_email

def handle_search_results_submission(selected_instruments: List[Dict], user_info: Dict[str, str], submission_notes: str = "", feedback_data: Dict = None):
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
            "feedback_data": feedback_data,
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
    send_submission_email(submission_data, [], feedback_data=submission_data.get('feedback_data'))


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


def handle_portfolio_submission(
    selected_instruments: List[Dict], 
    user_info: Dict, 
    submission_notes: str,
    feedback_data: Dict = None
) -> None:
    """
    Enhanced submission handler following existing submission.py patterns.
    Generates both instrument CSV and share transfer CSV with existing email flow.
    """
    from app.services.portfolio_service import PortfolioService
    import pandas as pd
    import io
    
    try:
        with st.spinner("Processing portfolio submission..."):
            user_name = user_info.get("user_name", "Unknown User")
            dt = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            safe_user_name = user_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            
            # Create submission data following existing structure
            submission_data = {
                "user_info": user_info,
                "search_context": {
                    "wallet": st.session_state.get("selected_wallet", "Unknown"),
                    "wallet_id": st.session_state.get("selected_wallet_id", ""),
                    "search_history": st.session_state.get("search_history", [])
                },
                "selected_instruments": selected_instruments,
                "submission_notes": submission_notes,
                "feedback_data": feedback_data,
                "portfolio_data": PortfolioService.get_all_portfolio_entries(),
                "submission_timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add PDF extraction metadata if available
            if 'pdf_extraction' in st.session_state:
                submission_data["pdf_extraction"] = {
                    "document_metadata": st.session_state['pdf_extraction'].get("document_metadata"),
                    "confidence_scores": st.session_state['pdf_extraction'].get("confidence_scores"),
                    "extraction_timestamp": st.session_state['pdf_extraction'].get("processing_timestamp"),
                    "extraction_notes": st.session_state['pdf_extraction'].get("extraction_notes", [])
                }
            
            # Generate share transfer CSV data
            share_transfer_data = PortfolioService.generate_share_transfer_data()
            
            # Send enhanced email using existing email patterns
            send_portfolio_submission_email(submission_data, share_transfer_data)
            
            # Generate PDF using existing infrastructure
            pdf_bytes = make_pdf(submission_data)
            
        # Success feedback using existing pattern
        st.success(f"Portfolio submission for **{user_name}** processed successfully!")
        st.balloons()

        # Download section using existing patterns
        if pdf_bytes:
            st.markdown("### Download Your Results")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"Portfolio_Report_{safe_user_name}_{dt}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with col2:
                # Generate regular instruments CSV using existing function
                instruments_csv = generate_instruments_csv(selected_instruments)
                st.download_button(
                    label="Download Instruments CSV",
                    data=instruments_csv,
                    file_name=f"Instruments_{safe_user_name}_{dt}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col3:
                # Generate share transfer CSV in exact target format
                share_transfer_csv = generate_share_transfer_csv(share_transfer_data)
                st.download_button(
                    label="Download Share Transfer CSV",
                    data=share_transfer_csv,
                    file_name=f"ShareTransfer_{safe_user_name}_{dt}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"Portfolio submission failed: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")

def generate_share_transfer_csv(share_transfer_data: List[Dict]) -> str:
    """Generate CSV content in exact target format using existing CSV patterns."""
    if not share_transfer_data:
        return ""
    
    import csv
    import io
    
    output = io.StringIO()
    
    # Exact column order from target CSV format
    fieldnames = [
        'SX/EE', 'User ID ', 'TrustAccountID', 'ShareCode', 'InstrumentID',
        'Qty', 'Base Cost ©', 'Excel Date', 'SettlementDate', 'Last Price',
        'BrokerID_From', 'BrokerID_To', 'Reference', '', ' '
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for record in share_transfer_data:
        writer.writerow(record)
    
    return output.getvalue()

def send_portfolio_submission_email(submission_data: Dict, share_transfer_data: List[Dict]) -> None:
    """
    Send portfolio submission email following existing email_sender.py patterns.
    """
    try:
        # Use existing email credentials pattern
        sender_email = st.secrets["email_credentials"]["email_address"]
        sender_password = st.secrets["email_credentials"]["app_password"]
        
        # Use existing dev mode pattern from email_sender.py
        if st.session_state.get("dev_mode", False):
            recipient_email = st.session_state.get("dev_recipient_email", "don.kruger123@gmail.com")
        else:
            recipient_email = "don.kruger123@gmail.com"
        
        # Extract user info following existing pattern
        user_info = submission_data.get("user_info", {})
        user_name = user_info.get("user_name", "Unknown User")
        user_id = user_info.get("user_id", "Unknown")
        
        # Create message following existing structure
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        import smtplib
        
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = f"Share Transfer Portfolio Submission - {user_name}"
        
        # Email body following existing format
        body = f"""
A new portfolio submission with share transfer data has been completed.

User Details:
• Name: {user_name}
• User ID: {user_id}
• Selected Wallet: {user_info.get('selected_wallet', 'N/A')}
• Submission Time: {submission_data.get('submission_timestamp', 'Unknown')}

Portfolio Summary:
• Total Instruments: {len(submission_data.get('selected_instruments', []))}
• Portfolio Entries: {len(share_transfer_data)}
• Additional Notes: {submission_data.get('submission_notes', 'None provided')}

"""
        
        # Add PDF extraction information if available
        pdf_extraction = submission_data.get('pdf_extraction')
        if pdf_extraction:
            body += f"""PDF Extraction Details:
• Document Type: {pdf_extraction.get('document_metadata', {}).get('document_type', 'Unknown')}
• Broker: {pdf_extraction.get('document_metadata', {}).get('broker_name', 'Unknown')}
• Confidence Score: {pdf_extraction.get('confidence_scores', {}).get('overall', 0):.0%}
• Extraction Time: {pdf_extraction.get('extraction_timestamp', 'Unknown')}

"""
        
        # Add feedback section if provided
        feedback_data = submission_data.get('feedback_data')
        if feedback_data and feedback_data.get('submitted'):
            from app.email_sender import format_feedback_section
            body += format_feedback_section(feedback_data)
        
        body += f"""Attachments:
• PDF Report: Complete portfolio summary
• Instruments CSV: Selected instruments details
• Share Transfer CSV: Portfolio data in target format

Please process according to share transfer procedures.

Regards,
Smart Instrument Finder System
"""
        
        msg.attach(MIMEText(body, "plain"))
        
        # Generate filenames following existing pattern
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_user_name = user_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        base_filename = f"Portfolio_{safe_user_name}_{timestamp}"
        
        # Attach PDF using existing pattern
        pdf_bytes = make_pdf(submission_data)
        pdf_part = MIMEBase("application", "octet-stream")
        pdf_part.set_payload(pdf_bytes)
        encoders.encode_base64(pdf_part)
        pdf_part.add_header(
            "Content-Disposition",
            f"attachment; filename={base_filename}.pdf"
        )
        msg.attach(pdf_part)
        
        # Attach instruments CSV
        instruments_csv = generate_instruments_csv(submission_data.get('selected_instruments', []))
        instruments_part = MIMEBase("application", "octet-stream")
        instruments_part.set_payload(instruments_csv.encode("utf-8"))
        encoders.encode_base64(instruments_part)
        instruments_part.add_header(
            "Content-Disposition",
            f"attachment; filename={base_filename}_instruments.csv"
        )
        msg.attach(instruments_part)
        
        # Attach share transfer CSV
        share_transfer_csv = generate_share_transfer_csv(share_transfer_data)
        transfer_part = MIMEBase("application", "octet-stream")
        transfer_part.set_payload(share_transfer_csv.encode("utf-8"))
        encoders.encode_base64(transfer_part)
        transfer_part.add_header(
            "Content-Disposition",
            f"attachment; filename={base_filename}_share_transfer.csv"
        )
        msg.attach(transfer_part)
        
        # Send email using existing pattern
        st.info(f"Attempting to send email to: {recipient_email}")
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            st.info("Email sent successfully via SMTP")
        
        st.success(f"Portfolio submission sent successfully!")
        st.info(f"Email sent to: {recipient_email}")
        st.info(f"PDF Report: {base_filename}.pdf")
        st.info(f"Instruments CSV: {base_filename}_instruments.csv")
        st.info(f"Share Transfer CSV: {base_filename}_share_transfer.csv")
        
    except Exception as e:
        st.error(f"Email sending failed: {str(e)}")
        st.error("Please check your email configuration in .streamlit/secrets.toml and try again.")

# Keep the original function for backward compatibility
def handle_submission(answers: Dict[str, Any], uploaded_files: List[Optional[st.runtime.uploaded_file_manager.UploadedFile]]):
    """Legacy submission handler - kept for backward compatibility."""
    # This is the original function, kept in case any legacy code still references it
    send_submission_email(answers, uploaded_files)