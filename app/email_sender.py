# app/email_sender.py

import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional

def send_submission_email(
    answers: Dict[str, Any],
    uploaded_files: List[Optional[st.runtime.uploaded_file_manager.UploadedFile]]
):
    """
    Constructs and sends an email with the Entity Onboarding form submission data and attachments.
    
    Args:
        answers: Complete form submission data including entity details and all sections
        uploaded_files: List of uploaded documents (ID/Passport copies, proof of address, etc.)
    """
    try:
        # --- Credentials ---
        try:
            sender_email = st.secrets["email_credentials"]["email_address"]
            sender_password = st.secrets["email_credentials"]["app_password"]
        except KeyError as ke:
            st.error(f"❌ Missing email credentials in secrets.toml: {ke}")
            return
        
        # --- Set the recipient email address here ---
        # In dev mode, allow configurable email; otherwise use default production email
        if st.session_state.get("dev_mode", False):
            # Dev mode: Allow user to configure email or use default
            dev_email = st.session_state.get("dev_recipient_email", "jpearse@purplegroup.co.za")
            recipient_email = dev_email
        else:
            # Production mode: Always use default email
            recipient_email = "jpearse@purplegroup.co.za"

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
        body += f"• Proof of address documents\n"
        body += f"• Declaration and signatory information\n\n"
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
            st.warning(f"⚠️ Could not generate CSV file: {csv_error}")
            # Continue without CSV attachment

        # --- Attach User Uploaded Files ---
        valid_uploads = [f for f in uploaded_files if f is not None]
        for uploaded_file in valid_uploads:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(uploaded_file.getvalue())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {uploaded_file.name}",
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
        
        st.success(f"✅ Entity Onboarding submission sent successfully!")
        st.info(f"📧 Email sent to: {recipient_email}")
        st.info(f"📎 PDF Summary: {base_filename}.pdf")
        st.info(f"📊 CSV Data File: {base_filename}.csv")
        if valid_uploads:
            st.info(f"📎 Supporting Documents: {len(valid_uploads)} file(s) attached")

    except Exception as e:
        st.error(f"❌ Failed to send Entity Onboarding submission email: {e}")
        st.error("Please check your email configuration in .streamlit/secrets.toml and try again.")