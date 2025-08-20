"""
Field Specifications and Validation System

This module provides structured field specifications with validation rules,
dependencies, and UI control definitions following the semantic specification.
"""

import json
import re
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field


@dataclass
class FieldSpec:
    """Structured field specification with validation and UI metadata."""
    
    field_name: str
    data_type: str
    required_rule: str = "optional"
    format_regex: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float, str]] = None
    max_value: Optional[Union[int, float, str]] = None
    ui_control: str = "input"
    controlled_list: Optional[str] = None
    options: Optional[List[str]] = None
    dependencies: Dict[str, Any] = field(default_factory=dict)
    validation: Optional[str] = None
    validation_message: Optional[str] = None
    example: Optional[str] = None
    help_text: Optional[str] = None


class FieldSpecificationManager:
    """Manager for field specifications and validation."""
    
    def __init__(self):
        self._field_specs = self._load_field_specifications()
        self._role_specs = self._load_role_specifications()
        self._entity_role_rules = self._load_entity_role_rules()
    
    def _load_field_specifications(self) -> Dict[str, FieldSpec]:
        """Load field specifications from JSON."""
        try:
            data_path = Path(__file__).parent / "data" / "field_specifications.json"
            with open(data_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            specs = {}
            for field_name, spec_data in data.get("standard_field_formatting_rules", {}).items():
                specs[field_name] = FieldSpec(
                    field_name=field_name,
                    **spec_data
                )
            
            return specs
            
        except Exception as e:
            print(f"Warning: Could not load field specifications: {e}")
            return {}
    
    def _load_role_specifications(self) -> Dict[str, Any]:
        """Load role specifications from JSON."""
        try:
            data_path = Path(__file__).parent / "data" / "role_specifications.json"
            with open(data_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Warning: Could not load role specifications: {e}")
            return {}
    
    def _load_entity_role_rules(self) -> Dict[str, Any]:
        """Load entity role rules from JSON."""
        try:
            data_path = Path(__file__).parent / "data" / "entity_role_rules.json"
            with open(data_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Warning: Could not load entity role rules: {e}")
            return {}
    
    def get_field_spec(self, field_name: str) -> Optional[FieldSpec]:
        """Get field specification by name."""
        return self._field_specs.get(field_name)
    
    def get_required_roles_for_entity_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get required roles for an entity type."""
        for rule in self._entity_role_rules.get("entity_role_rules", []):
            if rule["entity_type"] == entity_type:
                return rule.get("required_roles", [])
        return []
    
    def get_conditional_roles_for_entity_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get conditional roles for an entity type."""
        for rule in self._entity_role_rules.get("entity_role_rules", []):
            if rule["entity_type"] == entity_type:
                return rule.get("conditional_roles", [])
        return []
    
    def get_fields_for_role(self, role_id: str) -> List[Dict[str, Any]]:
        """Get field list for a specific role."""
        role_data = self._role_specs.get("natural_person_roles", {}).get(role_id)
        if role_data:
            return role_data.get("fields", [])
        return []
    
    def get_entity_fields(self) -> List[Dict[str, Any]]:
        """Get fields for entity details."""
        return self._role_specs.get("entity_fields", [])
    
    def validate_field_value(self, field_name: str, value: Any, context: Dict[str, Any] = None) -> Tuple[bool, List[str]]:
        """
        Validate a field value against its specification.
        
        Args:
            field_name: Name of the field
            value: Value to validate
            context: Additional context for dependency validation
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        spec = self.get_field_spec(field_name)
        if not spec:
            return True, []  # No spec = no validation
        
        errors = []
        context = context or {}
        
        # Check if field is required
        if self._is_field_required(spec, context) and self._is_empty_value(value):
            errors.append(f"{field_name} is required.")
            return False, errors
        
        # Skip validation for empty optional fields
        if self._is_empty_value(value) and not self._is_field_required(spec, context):
            return True, []
        
        # Data type validation
        if not self._validate_data_type(spec, value):
            errors.append(f"{field_name} has invalid data type.")
        
        # Format/regex validation
        if spec.format_regex and isinstance(value, str):
            if not re.match(spec.format_regex, value):
                errors.append(f"{field_name} has invalid format.")
        
        # Length validation
        if isinstance(value, str):
            if spec.min_length and len(value) < spec.min_length:
                errors.append(f"{field_name} must be at least {spec.min_length} characters.")
            if spec.max_length and len(value) > spec.max_length:
                errors.append(f"{field_name} must be no more than {spec.max_length} characters.")
        
        # Value range validation
        if spec.min_value:
            min_val = self._parse_dynamic_value(spec.min_value)
            if self._compare_values(value, min_val, "lt"):
                errors.append(f"{field_name} must be at least {min_val}.")
        
        if spec.max_value:
            max_val = self._parse_dynamic_value(spec.max_value)
            if self._compare_values(value, max_val, "gt"):
                errors.append(f"{field_name} must be no more than {max_val}.")
        
        # Special validation
        if spec.validation:
            validation_errors = self._perform_special_validation(spec, value)
            errors.extend(validation_errors)
        
        # Dependency validation
        dependency_errors = self._validate_dependencies(spec, value, context)
        errors.extend(dependency_errors)
        
        return len(errors) == 0, errors
    
    def _is_field_required(self, spec: FieldSpec, context: Dict[str, Any]) -> bool:
        """Check if field is required based on rule and context."""
        rule = spec.required_rule
        
        if rule == "always":
            return True
        elif rule == "optional":
            return False
        elif rule == "if_formally_registered":
            return context.get("is_formally_registered", False)
        elif rule == "if_registration_number_provided":
            return bool(context.get("registration_number", "").strip())
        elif rule == "if_entity_type_trust":
            return context.get("entity_type") == "TRUST"
        elif rule == "if_id_type_sa_id":
            return context.get("id_type") == "SA ID Number"
        elif rule == "if_id_type_foreign_id":
            return context.get("id_type") == "Foreign ID Number"
        elif rule == "if_id_type_passport":
            return context.get("id_type") == "Foreign Passport Number"
        elif rule == "if_country_south_africa":
            return context.get("country") == "South Africa" or context.get("country") == "ZA"
        
        return False
    
    def _is_empty_value(self, value: Any) -> bool:
        """Check if value is considered empty."""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, list) and len(value) == 0:
            return True
        return False
    
    def _validate_data_type(self, spec: FieldSpec, value: Any) -> bool:
        """Validate data type."""
        if self._is_empty_value(value):
            return True
        
        data_type = spec.data_type
        
        if data_type == "string":
            return isinstance(value, str)
        elif data_type == "integer":
            return isinstance(value, int)
        elif data_type == "decimal":
            return isinstance(value, (int, float))
        elif data_type == "date":
            return isinstance(value, (datetime.date, str))
        elif data_type == "datetime":
            return isinstance(value, (datetime.datetime, str))
        elif data_type == "boolean":
            return isinstance(value, bool)
        elif data_type == "email":
            return isinstance(value, str) and "@" in value
        elif data_type == "phone":
            return isinstance(value, str)
        elif data_type == "id_sa":
            return isinstance(value, str) and value.isdigit()
        elif data_type == "array":
            return isinstance(value, list)
        
        return True  # Unknown types pass validation
    
    def _parse_dynamic_value(self, value_expr: str) -> Any:
        """Parse dynamic value expressions like 'today-18years'."""
        if isinstance(value_expr, str):
            if value_expr == "today":
                return datetime.date.today()
            elif value_expr.startswith("today-") and "years" in value_expr:
                years = int(value_expr.split("-")[1].replace("years", ""))
                return datetime.date.today() - datetime.timedelta(days=365 * years)
            elif value_expr.startswith("today+") and "day" in value_expr:
                days = int(value_expr.split("+")[1].replace("day", "").replace("s", ""))
                return datetime.date.today() + datetime.timedelta(days=days)
        
        return value_expr
    
    def _compare_values(self, value1: Any, value2: Any, operator: str) -> bool:
        """Compare two values with given operator."""
        try:
            if operator == "lt":
                return value1 < value2
            elif operator == "gt":
                return value1 > value2
            elif operator == "eq":
                return value1 == value2
        except (TypeError, ValueError):
            return False
        
        return False
    
    def _perform_special_validation(self, spec: FieldSpec, value: Any) -> List[str]:
        """Perform special validation like Luhn check."""
        errors = []
        
        if spec.validation == "luhn_check" and isinstance(value, str):
            if not self._luhn_check(value):
                errors.append(f"{spec.field_name} failed Luhn check validation.")
        
        elif spec.validation == "phone_format" and isinstance(value, str):
            if not self._validate_phone_format(value):
                errors.append(f"{spec.field_name} has invalid phone format.")
        
        elif spec.validation == "postal_code_format" and isinstance(value, str):
            # This would need country context for proper validation
            pass
        
        return errors

    def _coerce_to_date(self, value: Any) -> Optional[datetime.date]:
        """Best-effort conversion of a spec value to a date instance.
        Handles dynamic expressions via _parse_dynamic_value and ISO dates (YYYY-MM-DD).
        """
        if value is None:
            return None
        # First resolve dynamic expressions like today/today-18years/today+1day
        resolved = self._parse_dynamic_value(value) if isinstance(value, str) else value
        # If already a date
        if isinstance(resolved, datetime.date):
            return resolved
        # If datetime -> date
        if isinstance(resolved, datetime.datetime):
            return resolved.date()
        # If string in ISO format
        if isinstance(resolved, str):
            try:
                return datetime.date.fromisoformat(resolved)
            except Exception:
                return None
        return None

    def get_date_bounds(self, field_name: str) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """Return (min_date, max_date) for a date field based on its specification.

        - Supports ISO dates (YYYY-MM-DD)
        - Supports dynamic expressions already handled by _parse_dynamic_value
        - If max_value is missing but equals to symbolic 'today' in other formats, resolves accordingly
        """
        spec = self.get_field_spec(field_name)
        if not spec:
            return None, None

        min_date = self._coerce_to_date(spec.min_value)
        max_date = self._coerce_to_date(spec.max_value)
        return min_date, max_date
    
    def _validate_dependencies(self, spec: FieldSpec, value: Any, context: Dict[str, Any]) -> List[str]:
        """Validate field dependencies."""
        errors = []
        
        for dep_field, dep_value in spec.dependencies.items():
            context_value = context.get(dep_field)
            
            if dep_value == "not_empty":
                if not context_value or (isinstance(context_value, str) and not context_value.strip()):
                    errors.append(f"{spec.field_name} depends on {dep_field} being provided.")
            elif dep_value == "validate_against_country":
                # This would implement country-specific phone validation
                pass
            elif isinstance(dep_value, str):
                if context_value != dep_value:
                    errors.append(f"{spec.field_name} is only required when {dep_field} is {dep_value}.")
        
        return errors
    
    def _luhn_check(self, number: str) -> bool:
        """Perform Luhn algorithm check (for SA ID numbers)."""
        if not number.isdigit() or len(number) != 13:
            return False
        
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10
        
        return luhn_checksum(number) == 0
    
    def _validate_phone_format(self, phone: str) -> bool:
        """Validate phone number format."""
        # Basic phone validation - can be enhanced
        digits_only = re.sub(r'\D', '', phone)
        return 6 <= len(digits_only) <= 15


# Global instance
_field_spec_manager = FieldSpecificationManager()


# ===== API FUNCTIONS =====

def get_field_specification_manager() -> FieldSpecificationManager:
    """Get the global field specification manager."""
    return _field_spec_manager

def get_field_spec(field_name: str) -> Optional[FieldSpec]:
    """Get field specification by name."""
    return _field_spec_manager.get_field_spec(field_name)

def validate_field(field_name: str, value: Any, context: Dict[str, Any] = None) -> Tuple[bool, List[str]]:
    """Validate a field value."""
    return _field_spec_manager.validate_field_value(field_name, value, context)

def get_required_roles_for_entity_type(entity_type: str) -> List[Dict[str, Any]]:
    """Get required roles for an entity type."""
    return _field_spec_manager.get_required_roles_for_entity_type(entity_type)

def get_fields_for_role(role_id: str) -> List[Dict[str, Any]]:
    """Get fields for a role."""
    return _field_spec_manager.get_fields_for_role(role_id)

def get_entity_fields() -> List[Dict[str, Any]]:
    """Get entity fields."""
    return _field_spec_manager.get_entity_fields()

def get_date_bounds(field_name: str) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
    """Get (min_date, max_date) bounds for a date field from specs."""
    return _field_spec_manager.get_date_bounds(field_name)


if __name__ == "__main__":
    # Test the field specifications
    print("=== Field Specifications Test ===")
    
    # Test field validation
    manager = get_field_specification_manager()
    
    print("\nTesting field validation:")
    
    # Test required field
    is_valid, errors = validate_field("entity_name", "", {})
    print(f"entity_name='': Valid={is_valid}, Errors={errors}")
    
    is_valid, errors = validate_field("entity_name", "Test Company", {})
    print(f"entity_name='Test Company': Valid={is_valid}, Errors={errors}")
    
    # Test SA ID validation
    is_valid, errors = validate_field("sa_id_number", "9001015009087", {"id_type": "SA ID Number"})
    print(f"SA ID validation: Valid={is_valid}, Errors={errors}")
    
    # Test email validation
    is_valid, errors = validate_field("email", "test@example.com", {})
    print(f"Email validation: Valid={is_valid}, Errors={errors}")
    
    print("\nEntity type roles:")
    roles = get_required_roles_for_entity_type("COMPANY")
    for role in roles:
        print(f"  {role}")
