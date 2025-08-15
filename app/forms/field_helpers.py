"""
Field helpers for form specifications.

This module provides helper functions to generate form fields with controlled list options.
"""

from app.forms.engine import Field
from app.controlled_lists import (
    get_source_of_funds_multiselect,
    get_industry_select,
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
        Field("date_of_registration", "Date of Registration / Establishment", "date", required=False),
        Field("source_of_funds", "Source of Funds", "multiselect", required=True,
              options=get_source_of_funds_multiselect()),
        Field("industry", "Industry", "select", required=True,
              options=get_industry_select())
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
