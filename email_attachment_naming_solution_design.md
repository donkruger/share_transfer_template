# Email Attachment Naming Solution Design

## 📋 Problem Statement

Currently, the Juristics ReFICA App email submission system attaches user-uploaded files with their original filenames, which do not align with the form section titles displayed in the UI. This creates confusion when recipients try to understand which document belongs to which section or person.

### Current Issues:
- **Attachment Names**: Users upload "IMG_1234.jpg", "scan001.pdf", etc.
- **Section Titles**: Form displays "Company Directors", "Authorised Representative", "Entity Documents", etc.
- **Disconnect**: No clear mapping between attachment names and their source sections
- **Confusion**: Recipients cannot easily identify which document belongs to which person or section

## 🎯 Solution Objectives

1. **Clear Identification**: Each attachment should clearly indicate its source section and purpose
2. **Consistent Naming**: Standardized naming convention across all entity types
3. **Person-Specific**: Individual uploads should be tied to specific people with identifiers
4. **Maintainable**: Solution should work with existing architecture without major refactoring
5. **Extensible**: Easy to extend for new components and document types

## 🏗️ Architecture Overview

### Core Concept: Enhanced Upload Metadata

Instead of returning raw `UploadedFile` objects, components will return enhanced metadata that includes:
- **Source Section Title**: The UI section where the file was uploaded
- **Document Type**: The specific document type (ID Document, Proof of Address, etc.)
- **Person Identifier**: For person-specific uploads (Name, ID number, etc.)
- **Entity Context**: Entity name and type for global context

### Data Structure Design

```python
@dataclass
class AttachmentMetadata:
    """Enhanced metadata for file attachments."""
    file: st.runtime.uploaded_file_manager.UploadedFile
    section_title: str          # "Company Directors", "Entity Documents", etc.
    document_type: str          # "ID Document", "Proof of Address", etc.
    person_identifier: str = "" # "John_Smith_Director_1", "Auth_Rep", etc.
    entity_context: str = ""    # "Acme_Corp_Company", etc.
    
    def generate_filename(self) -> str:
        """Generate standardized filename for email attachment."""
        # Implementation details below
```

## 🔧 Implementation Strategy

### Phase 1: Core Infrastructure

#### 1.1 Create Attachment Metadata System

**File**: `app/attachment_metadata.py`

```python
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
        parts.append(self._sanitize_filename_part(self.section_title))
        
        # Add person identifier if available
        if self.person_identifier:
            parts.append(self._sanitize_filename_part(self.person_identifier))
        
        # Add document type
        parts.append(self._sanitize_filename_part(self.document_type))
        
        # Get original file extension
        original_name = self.file.name
        if '.' in original_name:
            extension = original_name.split('.')[-1].lower()
        else:
            extension = 'bin'  # fallback for files without extension
        
        # Combine parts
        filename_base = '_'.join(parts)
        
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
            parts.append(entity_name)
        if entity_type:
            parts.append(entity_type)
        return '_'.join(self._sanitize_filename_part(part) for part in parts if part)
    
    def _sanitize_filename_part(self, text: str) -> str:
        """Sanitize text for use in filename."""
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
```

#### 1.2 Update Base Component Interface

**File**: `app/common_form_sections/base.py`

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
from app.attachment_metadata import AttachmentCollector

class SectionComponent(ABC):
    """Interface for reusable UI sections."""

    @abstractmethod
    def render(self, *, ns: str, instance_id: str, **config) -> None:
        """Draw widgets. Persist via your persist_* helpers."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        """Return a list of human-readable error strings (empty if ok)."""
        raise NotImplementedError

    @abstractmethod
    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        """
        Return: (payload_dict, uploads_list)
        - payload_dict: JSON-safe summary
        - uploads_list: list of UploadedFiles to attach in submission email
        """
        raise NotImplementedError
    
    def serialize_with_metadata(self, *, ns: str, instance_id: str, 
                               attachment_collector: AttachmentCollector, 
                               section_title: str, **config) -> Dict[str, Any]:
        """
        Enhanced serialization that adds attachments to collector with proper metadata.
        
        Args:
            attachment_collector: Collector to add attachments with metadata
            section_title: The UI section title for this component
            
        Returns:
            payload_dict: JSON-safe summary (same as serialize()[0])
        """
        # Default implementation calls existing serialize and adds to collector
        payload, uploads = self.serialize(ns=ns, instance_id=instance_id, **config)
        
        # Add uploads to collector with basic metadata
        for upload in uploads:
            if upload is not None:
                attachment_collector.add_attachment(
                    file=upload,
                    section_title=section_title,
                    document_type="Document",  # Generic fallback
                    person_identifier=""
                )
        
        return payload
```

### Phase 2: Component Updates

#### 2.1 Update Natural Persons Component

**File**: `app/common_form_sections/natural_persons.py`

Add the new serialization method:

```python
def serialize_with_metadata(self, *, ns: str, instance_id: str, 
                           attachment_collector: AttachmentCollector, 
                           section_title: str, **config) -> Dict[str, Any]:
    """Enhanced serialization with proper attachment naming."""
    
    role_label = config.get("role_label", "Person")
    count_key = inst_key(ns, instance_id, "count")
    n = st.session_state.get(count_key, 0)
    
    people = []
    
    if not n or n <= 0:
        return {"Count": 0, "Records": []}

    for i in range(n):
        # Get person details for identifier
        first_name = st.session_state.get(inst_key(ns, instance_id, f"first_name_{i}"), "")
        surname = st.session_state.get(inst_key(ns, instance_id, f"surname_{i}"), "")
        id_type = st.session_state.get(inst_key(ns, instance_id, f"id_type_{i}"), "")
        
        # Create person identifier
        name_parts = [part for part in [first_name, surname] if part.strip()]
        person_name = "_".join(name_parts) if name_parts else f"{role_label}_{i+1}"
        person_identifier = f"{person_name}_{role_label}_{i+1}"
        
        # Collect person data
        person_data = {
            # ... existing person data collection ...
        }
        people.append(person_data)
        
        # Add attachments with metadata
        if config.get("show_uploads", True):
            # ID Document
            id_doc = st.session_state.get(inst_key(ns, instance_id, f"id_doc_{i}"))
            if id_doc:
                doc_type = "ID_Document"
                if id_type == "SA ID Number":
                    doc_type = "SA_ID_Document"
                elif id_type == "Foreign Passport Number":
                    doc_type = "Passport_Document"
                elif id_type == "Foreign ID Number":
                    doc_type = "Foreign_ID_Document"
                
                attachment_collector.add_attachment(
                    file=id_doc,
                    section_title=section_title,
                    document_type=doc_type,
                    person_identifier=person_identifier
                )
            
            # Proof of Address (if enabled)
            if config.get("show_poa_uploads", True):
                poa_doc = st.session_state.get(inst_key(ns, instance_id, f"poa_doc_{i}"))
                if poa_doc:
                    attachment_collector.add_attachment(
                        file=poa_doc,
                        section_title=section_title,
                        document_type="Proof_of_Address",
                        person_identifier=person_identifier
                    )

    return {"Count": n, "Records": people}
```

#### 2.2 Update Authorised Representative Component

**File**: `app/common_form_sections/authorised_representative.py`

Add similar enhanced serialization:

```python
def serialize_with_metadata(self, *, ns: str, instance_id: str, 
                           attachment_collector: AttachmentCollector, 
                           section_title: str, **config) -> Dict[str, Any]:
    """Enhanced serialization with proper attachment naming."""
    
    # Get person details
    first_name = st.session_state.get(inst_key(ns, instance_id, "first_name"), "")
    last_name = st.session_state.get(inst_key(ns, instance_id, "last_name"), "")
    id_type = st.session_state.get(inst_key(ns, instance_id, "id_type"), "")
    
    # Create identifier
    name_parts = [part for part in [first_name, last_name] if part.strip()]
    person_identifier = "Auth_Rep"
    if name_parts:
        person_identifier = f"{'_'.join(name_parts)}_Auth_Rep"
    
    # Get existing payload
    payload, uploads = self.serialize(ns=ns, instance_id=instance_id, **config)
    
    # Add attachments with metadata (Note: AuthRep component doesn't currently have uploads,
    # but this prepares for future enhancement)
    for upload in uploads:
        if upload:
            attachment_collector.add_attachment(
                file=upload,
                section_title=section_title,
                document_type="Auth_Rep_Document",
                person_identifier=person_identifier
            )
    
    return payload
```

#### 2.3 Update Form Engine

**File**: `app/forms/engine.py`

Enhance the serialization process:

```python
from app.attachment_metadata import AttachmentCollector

def serialize_answers_with_metadata(spec: FormSpec, ns: str) -> Tuple[Dict[str, Any], AttachmentCollector]:
    """Enhanced serialization that returns attachment collector with metadata."""
    
    # Get entity context for attachments
    entity_name = st.session_state.get("entity_display_name", "")
    entity_type = spec.title
    
    attachment_collector = AttachmentCollector(entity_name, entity_type)
    answers: Dict[str, Any] = {"Entity Type": spec.title}
    
    for sec in spec.sections:
        sec_dict: Dict[str, Any] = {}
        
        # Handle simple fields
        for f in sec.fields:
            if f.kind == "info":
                continue
                
            val = st.session_state.get(ns_key(ns, f.key))
            
            if f.kind == "file":
                # Handle file fields from field helpers (e.g., entity documents)
                has_files = bool(val) if not f.accept_multiple else bool(val and len(val) > 0)
                sec_dict[f.label] = has_files
                
                if f.accept_multiple and isinstance(val, list):
                    for file_obj in val:
                        if file_obj:
                            attachment_collector.add_attachment(
                                file=file_obj,
                                section_title=sec.title,
                                document_type=f.label.replace(" ", "_"),
                                person_identifier=""
                            )
                elif val is not None:
                    attachment_collector.add_attachment(
                        file=val,
                        section_title=sec.title,
                        document_type=f.label.replace(" ", "_"),
                        person_identifier=""
                    )
            else:
                # Handle non-file fields
                if f.kind == "date" and val is not None:
                    try:
                        sec_dict[f.label] = val.strftime("%Y/%m/%d")
                    except Exception:
                        sec_dict[f.label] = val
                else:
                    sec_dict[f.label] = val

        # Handle component sections
        if sec.component_id:
            comp = get_component(sec.component_id)
            if comp:
                instance_id = sec.component_args.get("instance_id") or sec.title.lower().replace(" ", "_")
                component_kwargs = {k: v for k, v in sec.component_args.items() if k != "instance_id"}
                
                try:
                    # Try enhanced serialization first
                    if hasattr(comp, 'serialize_with_metadata'):
                        payload = comp.serialize_with_metadata(
                            ns=ns, 
                            instance_id=instance_id, 
                            attachment_collector=attachment_collector,
                            section_title=sec.title,
                            **component_kwargs
                        )
                    else:
                        # Fallback to traditional serialization
                        payload, comp_uploads = comp.serialize(ns=ns, instance_id=instance_id, **component_kwargs)
                        # Add uploads with basic metadata
                        for upload in comp_uploads or []:
                            if upload:
                                attachment_collector.add_attachment(
                                    file=upload,
                                    section_title=sec.title,
                                    document_type="Document",
                                    person_identifier=""
                                )
                    
                    sec_dict.update(payload if isinstance(payload, dict) else {})
                    
                except Exception as e:
                    st.error(f"❌ Error serializing component {sec.component_id}: {e}")
                    continue

        answers[sec.title] = sec_dict

    return answers, attachment_collector

# Backward compatibility function
def serialize_answers(spec: FormSpec, ns: str) -> Tuple[Dict[str, Any], List[Any]]:
    """Traditional serialization for backward compatibility."""
    answers, attachment_collector = serialize_answers_with_metadata(spec, ns)
    uploads = attachment_collector.get_legacy_upload_list()
    return answers, uploads
```

### Phase 3: Email System Integration

#### 3.1 Update Email Sender

**File**: `app/email_sender.py`

Add support for enhanced attachment metadata:

```python
from app.attachment_metadata import AttachmentCollector, AttachmentMetadata

def send_submission_email_with_metadata(
    answers: Dict[str, Any],
    attachment_collector: AttachmentCollector
):
    """Enhanced email sending with properly named attachments."""
    
    # ... existing email setup code ...
    
    # --- Attach User Uploaded Files with Enhanced Names ---
    attachments = attachment_collector.get_attachments_for_email()
    
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
    
    # ... rest of email sending code ...
    
    # Enhanced logging
    if attachments:
        st.info(f"📎 Enhanced Attachments: {len(attachments)} file(s) with descriptive names")
        for att in attachments[:5]:  # Show first 5 for brevity
            st.info(f"  • {att.generate_filename()}")
        if len(attachments) > 5:
            st.info(f"  • ... and {len(attachments) - 5} more")

# Backward compatibility wrapper
def send_submission_email(
    answers: Dict[str, Any],
    uploaded_files: List[Optional[st.runtime.uploaded_file_manager.UploadedFile]]
):
    """Backward compatibility wrapper."""
    # Create basic attachment collector for legacy calls
    attachment_collector = AttachmentCollector()
    
    for i, file in enumerate(uploaded_files):
        if file:
            attachment_collector.add_attachment(
                file=file,
                section_title="Legacy_Upload",
                document_type="Document",
                person_identifier=f"Upload_{i+1}"
            )
    
    send_submission_email_with_metadata(answers, attachment_collector)
```

#### 3.2 Update Submission Handler

**File**: `app/components/submission.py`

```python
def handle_submission(answers: Dict[str, Any], uploaded_files: List[Optional[st.runtime.uploaded_file_manager.UploadedFile]]):
    """Enhanced submission handling with proper attachment naming."""
    
    # Check for enhanced attachment support
    if hasattr(answers, '_attachment_collector'):
        # Use enhanced email sending
        attachment_collector = answers._attachment_collector
        send_submission_email_with_metadata(answers, attachment_collector)
    else:
        # Fall back to legacy email sending
        send_submission_email(answers, uploaded_files)
    
    # ... rest of submission handling ...
```

#### 3.3 Update Declaration Page

**File**: `app/pages/3_Declaration_and_Submit.py`

Update the payload reconstruction to use enhanced serialization:

```python
def reconstruct_payload():
    ns = current_namespace()
    spec = SPECS.get(ns)
    if not spec:
        st.error("The selected entity type is not configured.")
        st.stop()

    # Use enhanced serialization
    try:
        from app.forms.engine import serialize_answers_with_metadata
        answers, attachment_collector = serialize_answers_with_metadata(spec, ns)
        
        # Store attachment collector for submission handler
        answers._attachment_collector = attachment_collector
        
        # Get legacy upload list for backward compatibility
        uploads = attachment_collector.get_legacy_upload_list()
        
    except ImportError:
        # Fallback to traditional serialization
        from app.forms.engine import serialize_answers
        answers, uploads = serialize_answers(spec, ns)
    
    # ... rest of validation and metadata addition ...
    
    return answers, uploads
```

## 📊 Expected Results

### Before Implementation:
```
Email Attachments:
- IMG_1234.jpg
- scan001.pdf
- document.pdf
- photo.jpg
```

### After Implementation:
```
Email Attachments:
- Acme_Corp_Company_Company_Directors_John_Smith_Director_1_SA_ID_Document.jpg
- Acme_Corp_Company_Company_Directors_John_Smith_Director_1_Proof_of_Address.pdf
- Acme_Corp_Company_Entity_Documents_Certificate_of_Incorporation.pdf
- Acme_Corp_Company_Authorised_Representative_Jane_Doe_Auth_Rep_ID_Document.jpg
```

### Naming Convention:
```
{Entity_Name}_{Entity_Type}_{Section_Title}_{Person_Identifier}_{Document_Type}.{extension}
```

## 🧪 Testing Strategy

### Phase 1: Unit Testing
- Test `AttachmentMetadata.generate_filename()` with various inputs
- Test filename sanitization edge cases
- Test filename length limits

### Phase 2: Component Testing
- Test each component's `serialize_with_metadata()` method
- Verify correct person identifiers are generated
- Test with multiple people in same section

### Phase 3: Integration Testing
- Test full form submission with enhanced naming
- Verify backward compatibility with existing forms
- Test email attachment naming end-to-end

### Phase 4: User Acceptance Testing
- Verify attachment names are clear and helpful
- Test with different entity types and configurations
- Ensure no performance degradation

## 🚀 Migration Strategy

### Phase 1: Infrastructure (Week 1)
1. Implement `AttachmentMetadata` and `AttachmentCollector` classes
2. Update base component interface with optional enhanced method
3. Create unit tests for core functionality

### Phase 2: Component Updates (Week 2)
1. Update `NaturalPersonsComponent` with enhanced serialization
2. Update `AuthorisedRepresentativeComponent`
3. Update any other components with file uploads
4. Maintain backward compatibility

### Phase 3: Engine Integration (Week 3)
1. Update form engine with enhanced serialization
2. Update email sender with metadata support
3. Maintain legacy function wrappers
4. Integration testing

### Phase 4: Frontend Integration (Week 4)
1. Update declaration page to use enhanced serialization
2. Update submission handler
3. End-to-end testing
4. Performance testing

### Phase 5: Deployment & Monitoring (Week 5)
1. Deploy with feature flag for gradual rollout
2. Monitor attachment naming in production emails
3. Gather user feedback
4. Remove legacy code after validation

## 🔧 Maintenance Considerations

### Code Maintainability
- Clear separation between legacy and enhanced systems
- Comprehensive documentation for naming conventions
- Easy extension for new document types

### Performance Impact
- Minimal performance overhead (filename generation only)
- No additional database or external service calls
- Efficient string operations

### Future Enhancements
- Support for custom naming templates
- Integration with document management systems
- Automated attachment validation by name patterns

## 📋 Success Metrics

### Technical Metrics
- ✅ 100% of attachments have descriptive names
- ✅ Backward compatibility maintained
- ✅ No performance degradation
- ✅ Zero breaking changes to existing API

### User Experience Metrics
- ✅ Recipients can easily identify document sources
- ✅ Reduced confusion about attachment purposes
- ✅ Improved processing efficiency for form reviewers
- ✅ Enhanced audit trail for compliance

This solution provides a comprehensive approach to solving the attachment naming problem while maintaining the existing architecture's integrity and ensuring smooth migration.
