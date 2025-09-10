# app/utils/json_validators.py

from typing import Dict, List, Tuple
from pathlib import Path
import json

def validate_portfolio_json(json_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate portfolio JSON against schema for AI integration.
    
    Args:
        json_data: JSON data to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    try:
        import jsonschema
    except ImportError:
        # Fallback validation if jsonschema is not available
        return _basic_portfolio_validation(json_data)
    
    try:
        # Load schema
        schema_path = Path(__file__).parent.parent / "data" / "portfolio_schema.json"
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Validate against schema
        jsonschema.validate(json_data, schema)
        
        # Additional business logic validation
        errors = []
        
        # Check for duplicate instruments
        seen_instruments = set()
        for entry in json_data.get('portfolio_entries', []):
            identifier = entry.get('instrument_identifier', {})
            # Create a unique key from available identifiers
            key_parts = []
            for field in ['ticker', 'isin', 'instrument_id']:
                if identifier.get(field):
                    key_parts.append(f"{field}:{identifier[field]}")
            
            if key_parts:
                unique_key = "|".join(sorted(key_parts))
                if unique_key in seen_instruments:
                    errors.append(f"Duplicate instrument found: {identifier}")
                seen_instruments.add(unique_key)
        
        # Validate confidence scores
        metadata = json_data.get('metadata', {})
        if 'confidence_score' in metadata:
            score = metadata['confidence_score']
            if not (0 <= score <= 1):
                errors.append(f"Invalid confidence score: {score} (must be 0-1)")
        
        return len(errors) == 0, errors
        
    except jsonschema.ValidationError as e:
        return False, [f"Schema validation error: {e.message}"]
    except Exception as e:
        return False, [f"Validation error: {str(e)}"]

def _basic_portfolio_validation(json_data: Dict) -> Tuple[bool, List[str]]:
    """
    Basic validation when jsonschema is not available.
    """
    errors = []
    
    # Check required top-level fields
    if 'metadata' not in json_data:
        errors.append("Missing required field: metadata")
    if 'portfolio_entries' not in json_data:
        errors.append("Missing required field: portfolio_entries")
        
    if errors:
        return False, errors
    
    # Validate metadata
    metadata = json_data['metadata']
    if 'source' not in metadata:
        errors.append("Missing required metadata field: source")
    if 'extraction_timestamp' not in metadata:
        errors.append("Missing required metadata field: extraction_timestamp")
    
    # Validate portfolio entries
    entries = json_data['portfolio_entries']
    if not isinstance(entries, list):
        errors.append("portfolio_entries must be an array")
        return False, errors
    
    for i, entry in enumerate(entries):
        if 'instrument_identifier' not in entry:
            errors.append(f"Entry {i}: Missing instrument_identifier")
        if 'portfolio_data' not in entry:
            errors.append(f"Entry {i}: Missing portfolio_data")
            continue
            
        # Validate portfolio data required fields
        portfolio_data = entry['portfolio_data']
        required_fields = [
            'trust_account_id', 'quantity', 'base_cost', 
            'settlement_date', 'last_price', 'broker_from', 'broker_to'
        ]
        
        for field in required_fields:
            if field not in portfolio_data:
                errors.append(f"Entry {i}: Missing required field: {field}")
    
    return len(errors) == 0, errors

def validate_trust_account_id(account_id: str) -> Tuple[bool, str]:
    """Validate trust account ID format."""
    if not account_id or not account_id.strip():
        return False, "Trust Account ID is required"
    
    # Basic format validation (6-10 digits)
    import re
    if not re.match(r'^\d{6,10}$', account_id.strip()):
        return False, "Trust Account ID must be 6-10 digits"
    
    return True, ""

def validate_quantity(quantity: float) -> Tuple[bool, str]:
    """Validate share quantity."""
    if quantity == 0:
        return False, "Quantity cannot be zero"
    
    if abs(quantity) > 999999999:
        return False, "Quantity exceeds maximum allowed value"
    
    return True, ""

def validate_price(price: float, field_name: str) -> Tuple[bool, str]:
    """Validate price fields."""
    if price <= 0:
        return False, f"{field_name} must be greater than zero"
    
    if price > 99999999:
        return False, f"{field_name} exceeds maximum allowed value"
    
    return True, ""
