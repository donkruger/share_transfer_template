# app/csv_generator.py

import io
import csv
from typing import Dict, Any, List

def _flatten_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Flattens the nested 'answers' payload into a list of dictionaries,
    suitable for writing to a CSV in a long format.
    
    This handles complex nested structures including:
    - Simple key-value pairs
    - Sections with Records (Natural Persons, Juristic Entities)
    - Mixed data types and structures
    """
    flat_rows = []
    
    for section_title, section_data in data.items():
        if not isinstance(section_data, dict):
            # Handle top-level simple values like 'Entity Type'
            flat_rows.append({
                "Section": "Submission Details",
                "Record #": 1,
                "Field": section_title,
                "Value": str(section_data) if section_data is not None else ""
            })
            continue

        # Check for repeating records (e.g., Natural Persons, Juristic Entities)
        if "Records" in section_data and isinstance(section_data["Records"], list):
            records = section_data["Records"]
            if not records:  # Handle case with 0 records
                flat_rows.append({
                    "Section": section_title,
                    "Record #": 0,
                    "Field": "Count",
                    "Value": 0
                })
            else:
                for i, record in enumerate(records):
                    if isinstance(record, dict):
                        for field, value in record.items():
                            flat_rows.append({
                                "Section": section_title,
                                "Record #": i + 1,
                                "Field": field,
                                "Value": str(value) if value is not None else ""
                            })
        else:
            # Handle standard sections with key-value pairs
            for field, value in section_data.items():
                # Don't add the 'Records' key itself, as it's been processed
                if field == "Records":
                    continue
                flat_rows.append({
                    "Section": section_title,
                    "Record #": 1,
                    "Field": field,
                    "Value": str(value) if value is not None else ""
                })

    return flat_rows

def make_csv(payload: Dict[str, Any]) -> str:
    """
    Renders the captured answers payload to a CSV string.

    Args:
        payload: The complete dictionary of serialized answers from the form engine.

    Returns:
        A string containing the data in CSV format with headers:
        Section, Record #, Field, Value
        
    Example output format:
        Section,Record #,Field,Value
        Entity Details,1,Entity Name,Acme Corp Ltd
        Directors,1,Full Name,John Smith
        Directors,1,SA ID,1234567890123
        Directors,2,Full Name,Jane Doe
        Directors,2,Foreign ID,ABC123456
    """
    output = io.StringIO()
    
    flat_data = _flatten_data(payload)
    
    if not flat_data:
        # Return empty CSV with just headers if no data
        output.write("Section,Record #,Field,Value\n")
        return output.getvalue()

    # Define headers based on the keys of the flattened data
    headers = ["Section", "Record #", "Field", "Value"]
    writer = csv.DictWriter(output, fieldnames=headers)
    
    writer.writeheader()
    writer.writerows(flat_data)
    
    return output.getvalue()

def _sanitize_filename(name: str) -> str:
    """
    Sanitizes a string to be safe for use in filenames.
    
    Args:
        name: The original name string
        
    Returns:
        A sanitized string safe for filenames
    """
    import re
    # Replace invalid filename characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Replace spaces and other problematic chars
    sanitized = sanitized.replace(' ', '_').replace('-', '_')
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Limit length to reasonable filename size
    return sanitized[:50] if len(sanitized) > 50 else sanitized

def generate_csv_filename(entity_name: str, entity_type: str) -> str:
    """
    Generates a standardized CSV filename for the submission.
    
    Args:
        entity_name: The name of the entity
        entity_type: The type of entity
        
    Returns:
        A formatted filename string
    """
    import datetime
    
    safe_entity_name = _sanitize_filename(entity_name)
    safe_entity_type = _sanitize_filename(entity_type)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"Entity_Onboarding_Data_{safe_entity_name}_{safe_entity_type}_{timestamp}.csv"
