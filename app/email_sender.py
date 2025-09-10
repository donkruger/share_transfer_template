# app/email_sender.py

import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.attachment_metadata import AttachmentCollector

def format_feedback_section(feedback_data: Dict[str, Any]) -> str:
    """Format feedback data for email inclusion."""
    section = "--- USER FEEDBACK ---\n"
    section += f"Entity: {feedback_data.get('entity_name', 'N/A')}\n"
    section += f"Email: {feedback_data.get('email', 'N/A')}\n"
    section += f"Category: {feedback_data.get('category', 'N/A')}\n"
    section += f"Satisfaction: {feedback_data.get('satisfaction_rating', 'N/A')}/5\n"
    section += f"Message: {feedback_data.get('message', 'N/A')}\n"
    section += "--- END FEEDBACK ---\n\n"
    return section

def send_submission_email_with_metadata(
    answers: Dict[str, Any],
    attachment_collector: 'AttachmentCollector',
    feedback_data: Optional[Dict[str, Any]] = None
):
    """Enhanced email sending with properly named attachments."""
    
    try:
        # --- Credentials ---
        try:
            sender_email = st.secrets["email_credentials"]["email_address"]
            sender_password = st.secrets["email_credentials"]["app_password"]
        except KeyError as ke:
            st.error(f"Missing email credentials in secrets.toml: {ke}")
            return
        
        # --- Set the recipient email address here ---
        # In dev mode, allow configurable email; otherwise use default production email
        if st.session_state.get("dev_mode", False):
            # Dev mode: Allow user to configure email or use default
            dev_email = st.session_state.get("dev_recipient_email", "don.kruger123@gmail.com")
            recipient_email = dev_email
        else:
            # Production mode: Always use default email
            recipient_email = "don.kruger123@gmail.com"

        # --- Extract Entity Information ---
        entity_user_id = answers.get("Entity User ID", "Unknown")
        
        # Extract entity name from the correct path in the data structure
        entity_name = "Unknown Entity"
        entity_details = answers.get("Entity Details", {})
        if entity_details:
            # Try common field names for entity name
            entity_name = (entity_details.get("Legal / Registered Name") or 
                          entity_details.get("Entity Name") or 
                          entity_details.get("Trust Name") or
                          entity_details.get("Partnership Name") or
                          entity_details.get("CC Registered Name") or
                          st.session_state.get("entity_display_name", "Unknown Entity"))
        
        entity_type = st.session_state.get("entity_type", "Unknown Type")
        
        # --- Email Content ---
        subject = f"New Entity Onboarding Submission: {entity_name} ({entity_type})"

        body = f"A new Entity Onboarding form has been submitted for processing.\n\n"
        body += f"Entity Details:\n"
        body += f"• Entity Name: {entity_name}\n"
        body += f"• Entity Type: {entity_type}\n"
        body += f"• Entity User ID: {entity_user_id}\n\n"
        body += f"Please find the complete Entity Onboarding PDF summary, machine-readable CSV data file, and all supporting documents attached.\n\n"
        body += f"This submission includes:\n"
        body += f"• PDF Summary: Human-readable formatted summary of all form data\n"
        body += f"• CSV Data File: Machine-readable structured data for processing systems\n"
        body += f"• Entity details and registration information\n"
        body += f"• Physical address details\n"
        body += f"• Contact information\n"
        body += f"• Natural persons information (Directors, Members, Trustees, etc.)\n"
        body += f"• ID/Passport documentation\n"
        body += f"• Declaration and signatory information\n\n"
        
        # Add enhanced attachment summary
        attachments = attachment_collector.get_attachments_for_email()
        if attachments:
            body += f"Enhanced Attachments ({len(attachments)} files with descriptive names):\n"
            for att in attachments:
                body += f"• {att.generate_filename()}\n"
            body += "\n"
        
        # Add feedback section if provided
        if feedback_data and feedback_data.get('submitted'):
            body += format_feedback_section(feedback_data)
        
        body += f"Regards,\n"
        body += f"Entity Onboarding System\n"
        body += f"Satrix Asset Management"

        # --- Create the Email Message ---
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # --- Create standardized filenames ---
        safe_entity_name = entity_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"Entity_Onboarding_{safe_entity_name}_{timestamp}"

        # --- Attach PDF Summary ---
        from app.pdf_generator import make_pdf
        pdf_bytes = make_pdf(answers)
        pdf_part = MIMEBase("application", "octet-stream")
        pdf_part.set_payload(pdf_bytes)
        encoders.encode_base64(pdf_part)
        pdf_part.add_header(
            "Content-Disposition",
            f"attachment; filename={base_filename}.pdf",
        )
        msg.attach(pdf_part)

        # --- NEW: Attach CSV Data File ---
        try:
            from app.csv_generator import make_csv
            csv_string = make_csv(answers)
            csv_part = MIMEBase("application", "octet-stream")
            csv_part.set_payload(csv_string.encode("utf-8"))  # Encode the string to bytes
            encoders.encode_base64(csv_part)
            csv_part.add_header(
                "Content-Disposition",
                f"attachment; filename={base_filename}.csv",
            )
            msg.attach(csv_part)
        except Exception as csv_error:
            st.warning(f"Could not generate CSV file: {csv_error}")
            # Continue without CSV attachment

        # --- Attach User Uploaded Files with Enhanced Names ---
        for attachment_metadata in attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_metadata.file.getvalue())
            encoders.encode_base64(part)
            
            # Use enhanced filename
            enhanced_filename = attachment_metadata.generate_filename()
            
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={enhanced_filename}",
            )
            msg.attach(part)

        # --- Send the Email ---
        # Note: Ensure the sender email is configured for SMTP access.
        # For Gmail/Google Workspace accounts, use smtp.gmail.com
        # For other providers, update the SMTP server address accordingly.
        st.info(f"📧 Attempting to send email to: {recipient_email}")
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            st.info("📧 Email sent successfully via SMTP")
        
        st.success(f"Entity Onboarding submission sent successfully!")
        st.info(f"📧 Email sent to: {recipient_email}")
        st.info(f"📎 PDF Summary: {base_filename}.pdf")
        st.info(f"CSV Data File: {base_filename}.csv")
        
        # Enhanced attachment logging
        if attachments:
            st.info(f"📎 Enhanced Attachments: {len(attachments)} file(s) with descriptive names")
            for att in attachments[:5]:  # Show first 5 for brevity
                st.info(f"  • {att.generate_filename()}")
            if len(attachments) > 5:
                st.info(f"  • ... and {len(attachments) - 5} more")

    except Exception as e:
        st.error(f"Failed to send Entity Onboarding submission email: {e}")
        st.error("Please check your email configuration in .streamlit/secrets.toml and try again.")


def send_submission_email(
    answers: Dict[str, Any],
    uploaded_files: List[Optional[st.runtime.uploaded_file_manager.UploadedFile]]
):
    """
    Backward compatibility wrapper for legacy email sending.
    
    Args:
        answers: Complete form submission data including entity details and all sections
        uploaded_files: List of uploaded documents (ID/Passport copies, etc.)
    """
    # Check if answers has an attachment collector (from enhanced serialization)
    if hasattr(answers, '_attachment_collector'):
        # Use enhanced email sending
        attachment_collector = answers._attachment_collector
        send_submission_email_with_metadata(answers, attachment_collector)
        return
    
    # Create basic attachment collector for legacy calls
    from app.attachment_metadata import AttachmentCollector
    attachment_collector = AttachmentCollector()
    
    for i, file in enumerate(uploaded_files or []):
        if file:
            attachment_collector.add_attachment(
                file=file,
                section_title="Legacy_Upload",
                document_type="Document",
                person_identifier=f"Upload_{i+1}"
            )
    
    send_submission_email_with_metadata(answers, attachment_collector)