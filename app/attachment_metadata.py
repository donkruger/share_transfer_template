"""
Attachment Metadata System for Enhanced Email Attachment Naming

This module provides classes and utilities for managing file attachments with 
enhanced metadata, enabling descriptive and organized attachment naming in 
email submissions.
"""

from dataclasses import dataclass
from typing import List, Optional
import streamlit as st
import re


@dataclass
class AttachmentMetadata:
    """Enhanced metadata for file attachments with standardized naming."""
    
    file: st.runtime.uploaded_file_manager.UploadedFile
    section_title: str
    document_type: str
    person_identifier: str = ""
    entity_context: str = ""
    
    def _sanitize_filename_part(self, text: str) -> str:
        """Sanitize text for use in filename."""
        if not text:
            return ""
        
        # Remove special characters, keep alphanumeric and underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_\s-]', '', text)
        # Replace spaces and hyphens with underscores
        sanitized = re.sub(r'[\s-]+', '_', sanitized)
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Strip leading/trailing underscores
        return sanitized.strip('_')
    
    def generate_filename(self) -> str:
        """Generate standardized filename for email attachment."""
        parts = []
        
        # Add entity context if available
        if self.entity_context:
            parts.append(self._sanitize_filename_part(self.entity_context))
        
        # Add section title
        if self.section_title:
            parts.append(self._sanitize_filename_part(self.section_title))
        
        # Add person identifier if available
        if self.person_identifier:
            parts.append(self._sanitize_filename_part(self.person_identifier))
        
        # Add document type
        if self.document_type:
            parts.append(self._sanitize_filename_part(self.document_type))
        
        # Get original file extension
        original_name = self.file.name
        if '.' in original_name:
            extension = original_name.split('.')[-1].lower()
        else:
            extension = 'bin'  # fallback for files without extension
        
        # Combine parts
        filename_base = '_'.join(part for part in parts if part)
        
        # Fallback if no parts generated
        if not filename_base:
            filename_base = "Document"
        
        # Ensure filename isn't too long (limit to 200 chars before extension)
        if len(filename_base) > 200:
            filename_base = filename_base[:200].rstrip('_')
        
        return f"{filename_base}.{extension}"


class AttachmentCollector:
    """Utility class to collect and manage attachment metadata."""
    
    def __init__(self, entity_name: str = "", entity_type: str = ""):
        self.attachments: List[AttachmentMetadata] = []
        self.entity_context = self._create_entity_context(entity_name, entity_type)
    
    def _create_entity_context(self, entity_name: str, entity_type: str) -> str:
        """Create entity context string."""
        parts = []
        if entity_name:
            parts.append(self._sanitize_filename_part(entity_name))
        if entity_type:
            parts.append(self._sanitize_filename_part(entity_type))
        return '_'.join(part for part in parts if part)
    
    def _sanitize_filename_part(self, text: str) -> str:
        """Sanitize text for use in filename."""
        if not text:
            return ""
        
        sanitized = re.sub(r'[^a-zA-Z0-9_\s-]', '', text)
        sanitized = re.sub(r'[\s-]+', '_', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized.strip('_')
    
    def add_attachment(self, file: st.runtime.uploaded_file_manager.UploadedFile,
                      section_title: str, document_type: str, 
                      person_identifier: str = "") -> None:
        """Add an attachment with metadata."""
        if file is not None:
            metadata = AttachmentMetadata(
                file=file,
                section_title=section_title,
                document_type=document_type,
                person_identifier=person_identifier,
                entity_context=self.entity_context
            )
            self.attachments.append(metadata)
    
    def get_attachments_for_email(self) -> List[AttachmentMetadata]:
        """Get all attachments ready for email sending."""
        return [att for att in self.attachments if att.file is not None]
    
    def get_legacy_upload_list(self) -> List[st.runtime.uploaded_file_manager.UploadedFile]:
        """Get traditional upload list for backward compatibility."""
        return [att.file for att in self.attachments if att.file is not None]
    
    def get_attachment_count(self) -> int:
        """Get count of valid attachments."""
        return len(self.get_attachments_for_email())
    
    def clear_attachments(self) -> None:
        """Clear all attachments."""
        self.attachments.clear()
    
    def get_attachment_summary(self) -> List[str]:
        """Get a summary of attachment filenames for logging/display."""
        return [att.generate_filename() for att in self.get_attachments_for_email()]


# Utility functions for common attachment patterns

def sanitize_document_label(label: str) -> str:
    """Sanitize a document label for use in filename."""
    if not label:
        return "Document"
    
    # Remove common prefixes/suffixes that add noise
    cleaned = label.strip()
    
    # Replace common patterns
    replacements = {
        "Copy of the ": "",
        "Copy of ": "",
        "Document ": "",
        "Certificate of ": "Certificate_",
        "Proof of ": "Proof_of_",
        "Notice of ": "Notice_of_",
        " / ": "_or_",
        " OR ": "_or_",
        " AND ": "_and_",
        "(": "",
        ")": "",
        ",": "",
        ":": "",
        ";": "",
    }
    
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    # Apply standard sanitization
    sanitized = re.sub(r'[^a-zA-Z0-9_\s-]', '', cleaned)
    sanitized = re.sub(r'[\s-]+', '_', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized.strip('_') or "Document"


# Test function for development
def test_attachment_metadata():
    """Test function to validate attachment metadata functionality."""
    import io
    
    # Create a mock UploadedFile-like object for testing
    class MockUploadedFile:
        def __init__(self, name: str, content: bytes = b"test"):
            self.name = name
            self.content = content
        
        def getvalue(self):
            return self.content
    
    # Test basic functionality
    collector = AttachmentCollector("Acme Corp", "Company")
    
    # Test file addition
    mock_file = MockUploadedFile("scan.pdf")
    collector.add_attachment(
        file=mock_file,
        section_title="Company Directors",
        document_type="SA_ID_Document",
        person_identifier="John_Smith_Director_1"
    )
    
    # Test filename generation
    attachments = collector.get_attachments_for_email()
    if attachments:
        expected_name = "Acme_Corp_Company_Company_Directors_John_Smith_Director_1_SA_ID_Document.pdf"
        generated_name = attachments[0].generate_filename()
        print(f"Expected: {expected_name}")
        print(f"Generated: {generated_name}")
        print(f"Match: {expected_name == generated_name}")
    
    return collector


if __name__ == "__main__":
    # Run tests when file is executed directly
    test_attachment_metadata()
