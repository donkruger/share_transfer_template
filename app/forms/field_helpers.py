"""
Field helpers for form specifications.

This module provides helper functions to generate form fields with controlled list options.
"""

from app.forms.engine import Field
from app.document_requirements import get_document_upload_schema
from app.controlled_lists_enhanced import (
    get_source_of_funds_options,
    get_industry_options,
    get_countries
)

def create_entity_details_fields(entity_name_label: str = "Entity Name (Registered Name of Organisation / Entity)", include_trust_fields: bool = False):
    """
    Create the standard entity details fields that are common across all entity types.
    
    Args:
        entity_name_label: Custom label for the entity name field
        include_trust_fields: Whether to include Trust-specific fields in the correct position
        
    Returns:
        List of Field objects for entity details section
    """
    fields = [
        Field("entity_name", entity_name_label, "text", required=True)
    ]
    
    # Add Trust-specific fields if needed
    if include_trust_fields:
        fields.extend(create_trust_specific_fields())
    
    # Add remaining standard fields
    fields.extend([
        Field("trading_name", "Trading Name (Only if different from Registered Name)", "text", required=False),
        Field("registration_number", "Registration Number", "text", required=False),
        Field("country_of_registration", "Country of Registration", "select", required=False, 
              options=get_countries()),
        Field("date_of_registration", "Date of Registration / Establishment", "date", required=True),
        Field("source_of_funds", "Source of Funds", "select", required=True,
              options=get_source_of_funds_options(include_empty=True, return_codes=False)),
        Field("industry", "Industry", "select", required=True,
              options=get_industry_options(include_empty=True, return_codes=False))
    ])
    
    return fields

def create_trust_specific_fields():
    """
    Create Trust-specific fields (Masters Office).
    
    Returns:
        List of Field objects for Trust-specific requirements
    """
    return [
        Field("masters_office", "Masters Office where the Trust was registered", "text", required=True)
    ]

def create_entity_document_upload_fields(entity_type_code: str):
    """
    Create file upload fields for entity-level document requirements based on
    app/data/document_requirements.json for the given entity type code
    (e.g., 'COMPANY', 'TRUST', 'PARTNERSHIP', 'CLOSED_CORPORATION').

    Returns:
        List[Field]: File fields with required flags according to the spec
    """
    fields = []
    try:
        schema = get_document_upload_schema(entity_type_code)
        
        # Add a friendly message card about attachment size limits
        # This will be rendered as an info field in the form engine
        fields.append(Field(
            "attachment_size_info", 
            "📎 **Document Upload Guidelines**", 
            "info", 
            required=False,
            help_text="Please ensure your total attachment size (across all atachment fields) do not exceed 25MB, otherwise the submission may fail."
        ))
        
        for doc in schema.get("entity_documents", []):
            key = doc.get("document_code", "").lower()
            label = doc.get("description", key)
            required = bool(doc.get("required", False))
            fields.append(Field(key, label, "file", required=required))
    except Exception:
        # Fail quietly; no fields if schema cannot be loaded
        return []
    return fields
