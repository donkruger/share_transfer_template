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
        sender_email = st.secrets["email_credentials"]["email_address"]
        sender_password = st.secrets["email_credentials"]["app_password"]
        
        # --- Set the recipient email address here ---
        recipient_email = "jpearse@purplegroup.co.za" # <-- CHANGE THIS LINE

        # --- Extract Entity Information ---
        entity_user_id = answers.get("Entity User ID", "Unknown")
        entity_name = answers.get("Entity Details", {}).get("Entity Name", "Unknown Entity")
        entity_type = st.session_state.get("entity_type", "Unknown Type")
        
        # --- Email Content ---
        subject = f"New Entity Onboarding Submission: {entity_name} ({entity_type})"

        body = f"A new Entity Onboarding form has been submitted for processing.\n\n"
        body += f"Entity Details:\n"
        body += f"• Entity Name: {entity_name}\n"
        body += f"• Entity Type: {entity_type}\n"
        body += f"• Entity User ID: {entity_user_id}\n\n"
        body += f"Please find the complete Entity Onboarding PDF summary and all supporting documents attached.\n\n"
        body += f"This submission includes:\n"
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

        # --- Attach PDF Summary (already generated) ---
        from app.pdf_generator import make_pdf
        pdf_bytes = make_pdf(answers)
        part = MIMEBase("application", "octet-stream")
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        
        # Create a safe filename using entity name and current timestamp
        safe_entity_name = entity_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Entity_Onboarding_{safe_entity_name}_{timestamp}.pdf"
        
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={filename}",
        )
        msg.attach(part)

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
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        st.success(f"✅ Entity Onboarding submission sent successfully!")
        st.info(f"📧 Email sent to: {recipient_email}")
        st.info(f"📎 PDF filename: {filename}")
        if valid_uploads:
            st.info(f"📎 {len(valid_uploads)} supporting document(s) attached")

    except Exception as e:
        st.error(f"❌ Failed to send Entity Onboarding submission email: {e}")
        st.error("Please check your email configuration in .streamlit/secrets.toml and try again.")