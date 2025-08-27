"""
Enhanced Controlled Lists for Entity Onboarding System

This module provides structured controlled lists with codes, labels, and metadata
following the semantic specification requirements.

Schema format for controlled lists:
- code: string (stored in database/payload)
- label: string (displayed to user) 
- is_active: bool (for enabling/disabling options)
- sort_order: int (for custom ordering)
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional


class ControlledListManager:
    """Manager class for all controlled lists with structured data."""
    
    def __init__(self):
        self._controlled_lists = self._load_controlled_lists()
        self._countries = self._load_countries_from_csv()
        self._country_dial_codes = self._load_country_dial_codes()
    
    def _load_controlled_lists(self) -> Dict[str, Any]:
        """Load structured controlled lists from JSON file."""
        try:
            data_path = Path(__file__).parent / "data" / "controlled_lists.json"
            with open(data_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Warning: Could not load controlled lists: {e}")
            return {}
    
    def _load_countries_from_csv(self) -> List[Dict[str, str]]:
        """Load countries from CSV file and return structured list."""
        try:
            csv_path = Path(__file__).parent / "common_form_sections" / "CountryList.csv"
            countries = []
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                country_data = []
                
                for row in reader:
                    country_name = row.get('Country Name', '').strip()
                    iso_code = row.get('Country ISO code', '').strip()
                    
                    if country_name and country_name != '':
                        country_data.append({
                            "code": iso_code or country_name.upper().replace(' ', '_'),
                            "label": country_name,
                            "iso_alpha2": iso_code,
                            "is_active": True,
                            "sort_order": 999  # Will be overridden for SA
                        })
                
                # Sort alphabetically by label
                country_data.sort(key=lambda x: x["label"])
                
                # Add empty option first
                countries.append({
                    "code": "",
                    "label": "",
                    "iso_alpha2": "",
                    "is_active": True,
                    "sort_order": 0
                })
                
                # Prioritize South Africa
                sa_country = None
                for country in country_data:
                    if country["label"] == "South Africa":
                        sa_country = country
                        break
                
                if sa_country:
                    country_data.remove(sa_country)
                    sa_country["sort_order"] = 1
                    countries.append(sa_country)
                
                # Add all other countries
                for i, country in enumerate(country_data):
                    country["sort_order"] = i + 2
                    countries.append(country)
                
            return countries
            
        except Exception as e:
            print(f"Warning: Could not load countries from CSV: {e}")
            # Fallback to basic country list
            return [
                {"code": "", "label": "", "iso_alpha2": "", "is_active": True, "sort_order": 0},
                {"code": "ZA", "label": "South Africa", "iso_alpha2": "ZA", "is_active": True, "sort_order": 1},
                {"code": "GB", "label": "United Kingdom", "iso_alpha2": "GB", "is_active": True, "sort_order": 2},
                {"code": "US", "label": "United States", "iso_alpha2": "US", "is_active": True, "sort_order": 3},
            ]

    def _load_country_dial_codes(self) -> Dict[str, str]:
        """Load country dialing codes from CountryListV2.csv (label -> "+code")."""
        dial_map: Dict[str, str] = {}
        try:
            csv_path = Path(__file__).parent / "common_form_sections" / "CountryListV2.csv"
            if not csv_path.exists():
                return dial_map
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    label = (row.get('Country Name') or '').strip()
                    dial_col = (row.get('Dialing Code') or '').strip()
                    # Extract trailing +NN or +N... pattern
                    dial_code = ""
                    if dial_col:
                        # Find last token starting with '+'
                        parts = dial_col.split()
                        for token in reversed(parts):
                            if token.startswith('+'):
                                dial_code = token
                                break
                    if label and dial_code:
                        dial_map[label] = dial_code
            return dial_map
        except Exception as e:
            print(f"Warning: Could not load CountryListV2.csv dialing codes: {e}")
            return dial_map
    
    def get_list_options(self, list_name: str, include_empty: bool = True, 
                        return_codes: bool = False, with_description: bool = False) -> List[str]:
        """
        Get options for a controlled list.
        
        Args:
            list_name: Name of the controlled list
            include_empty: Whether to include empty option
            return_codes: If True, return codes; if False, return labels
            with_description: If True, combines label and description for display
            
        Returns:
            List of strings (either codes or labels)
        """
        if list_name == "countries":
            items = self._countries
        else:
            items = self._controlled_lists.get(list_name, [])
        
        # Filter active items and sort
        active_items = [item for item in items if item.get("is_active", True)]
        active_items.sort(key=lambda x: x.get("sort_order", 999))
        
        # Extract codes or labels with optional descriptions
        if return_codes:
            options = [item["code"] for item in active_items]
        else:
            options = []
            for item in active_items:
                if with_description and item.get("description"):
                    display_text = f"{item['label']} – {item['description']}"
                    options.append(display_text)
                else:
                    options.append(item["label"])
        
        # Handle empty option
        if not include_empty and options and options[0] == "":
            options = options[1:]
        elif include_empty and (not options or options[0] != ""):
            options.insert(0, "")
            
        return options
    
    def get_list_mapping(self, list_name: str) -> Dict[str, str]:
        """
        Get mapping from codes to labels for a controlled list.
        
        Returns:
            Dict mapping codes to labels
        """
        if list_name == "countries":
            items = self._countries
        else:
            items = self._controlled_lists.get(list_name, [])
        
        return {item["code"]: item["label"] for item in items if item.get("is_active", True)}
    
    def get_label_for_code(self, list_name: str, code: str) -> str:
        """Get label for a specific code in a controlled list."""
        mapping = self.get_list_mapping(list_name)
        return mapping.get(code, code)  # Return code if label not found
    
    def get_code_for_label(self, list_name: str, label: str) -> str:
        """Get code for a specific label in a controlled list."""
        mapping = self.get_list_mapping(list_name)
        reverse_mapping = {v: k for k, v in mapping.items()}
        return reverse_mapping.get(label, label)  # Return label if code not found


# Global instance
_controlled_list_manager = ControlledListManager()


# ===== ENHANCED API FUNCTIONS =====

def get_source_of_funds_options(include_empty: bool = False, return_codes: bool = False) -> List[str]:
    """Get Source of Funds options."""
    return _controlled_list_manager.get_list_options("source_of_funds", include_empty, return_codes)

def get_source_of_funds_multiselect() -> List[str]:
    """Get Source of Funds options for multiselect (labels, no empty option)."""
    return _controlled_list_manager.get_list_options("source_of_funds", include_empty=False, return_codes=False)

def get_industry_options(include_empty: bool = True, return_codes: bool = False) -> List[str]:
    """Get Industry options."""
    return _controlled_list_manager.get_list_options("industry", include_empty, return_codes)

def get_member_role_options(include_empty: bool = True, return_codes: bool = False) -> List[str]:
    """Get Member Role options."""
    return _controlled_list_manager.get_list_options("member_roles", include_empty, return_codes)

def get_member_role_select() -> List[str]:
    """Get Member Role options for select widgets."""
    return get_member_role_options(include_empty=True, return_codes=False)

def get_title_options(include_empty: bool = True, return_codes: bool = False) -> List[str]:
    """Get Title options."""
    return _controlled_list_manager.get_list_options("titles", include_empty, return_codes)

def get_gender_options(include_empty: bool = True, return_codes: bool = False) -> List[str]:
    """Get Gender options."""
    return _controlled_list_manager.get_list_options("gender", include_empty, return_codes)

def get_marital_status_options(include_empty: bool = True, return_codes: bool = False) -> List[str]:
    """Get Marital Status options."""
    return _controlled_list_manager.get_list_options("marital_status", include_empty, return_codes)

def get_entity_types(include_empty: bool = False, return_codes: bool = False) -> List[str]:
    """Get Entity Type options."""
    return _controlled_list_manager.get_list_options("entity_types", include_empty, return_codes)

# ===== FATCA CONTROLLED LISTS =====

def get_fatca_classifications(include_empty: bool = False, return_codes: bool = False) -> List[str]:
    """Get FATCA Classification options."""
    return _controlled_list_manager.get_list_options("fatca_classifications", include_empty, return_codes)

def get_us_person_types(include_empty: bool = False, return_codes: bool = False) -> List[str]:
    """Get US Person Type options."""
    return _controlled_list_manager.get_list_options("us_person_types", include_empty, return_codes)

def get_ffi_categories(include_empty: bool = False, return_codes: bool = False) -> List[str]:
    """Get FFI Category options."""
    return _controlled_list_manager.get_list_options("ffi_categories", include_empty, return_codes)

def get_nffe_types(include_empty: bool = False, return_codes: bool = False) -> List[str]:
    """Get NFFE Type options."""
    return _controlled_list_manager.get_list_options("nffe_types", include_empty, return_codes)

# ===== CRS CONTROLLED LISTS =====

def get_crs_classifications(include_empty: bool = False, return_codes: bool = False) -> List[str]:
    """Get CRS Classification options."""
    return _controlled_list_manager.get_list_options("crs_classifications", include_empty, return_codes)

def get_investment_entity_types(include_empty: bool = False, return_codes: bool = False) -> List[str]:
    """Get Investment Entity Type options."""
    return _controlled_list_manager.get_list_options("investment_entity_types", include_empty, return_codes)

def get_tin_options(include_empty: bool = False, return_codes: bool = False) -> List[str]:
    """Get TIN Options for controlling persons."""
    return _controlled_list_manager.get_list_options("tin_options", include_empty, return_codes)

# ===== ENHANCED FATCA & CRS FUNCTIONS WITH DESCRIPTIONS =====

def get_fatca_classifications_with_descriptions(include_empty: bool = False) -> List[str]:
    """Get FATCA Classification options with descriptive text."""
    return _controlled_list_manager.get_list_options("fatca_classifications", include_empty, return_codes=False, with_description=True)

def get_us_person_types_with_descriptions(include_empty: bool = False) -> List[str]:
    """Get US Person Type options with descriptive text."""
    return _controlled_list_manager.get_list_options("us_person_types", include_empty, return_codes=False, with_description=True)

def get_ffi_categories_with_descriptions(include_empty: bool = False) -> List[str]:
    """Get FFI Category options with descriptive text."""
    return _controlled_list_manager.get_list_options("ffi_categories", include_empty, return_codes=False, with_description=True)

def get_nffe_types_with_descriptions(include_empty: bool = False) -> List[str]:
    """Get NFFE Type options with descriptive text."""
    return _controlled_list_manager.get_list_options("nffe_types", include_empty, return_codes=False, with_description=True)

def get_crs_classifications_with_descriptions(include_empty: bool = False) -> List[str]:
    """Get CRS Classification options with descriptive text."""
    return _controlled_list_manager.get_list_options("crs_classifications", include_empty, return_codes=False, with_description=True)

def get_investment_entity_types_with_descriptions(include_empty: bool = False) -> List[str]:
    """Get Investment Entity Type options with descriptive text."""
    return _controlled_list_manager.get_list_options("investment_entity_types", include_empty, return_codes=False, with_description=True)

def get_tin_options_with_descriptions(include_empty: bool = False) -> List[str]:
    """Get TIN Options with descriptive text."""
    return _controlled_list_manager.get_list_options("tin_options", include_empty, return_codes=False, with_description=True)

def get_countries(include_empty: bool = True, return_codes: bool = False) -> List[str]:
    """Get comprehensive list of Country options with South Africa prioritized."""
    return _controlled_list_manager.get_list_options("countries", include_empty, return_codes)

def get_dial_code_for_country_label(country_label: str) -> str:
    """Return the international dialing code (e.g., "+27") for a given country label.
    Falls back to empty string if unknown.
    """
    try:
        mapping = _controlled_list_manager._country_dial_codes  # internal map loaded from V2 CSV
        return mapping.get((country_label or '').strip(), "")
    except Exception:
        return ""


# ===== BACKWARD COMPATIBILITY FUNCTIONS =====
# These maintain compatibility with existing code

def get_source_of_funds_select():
    """Backward compatibility: Get Source of Funds options for select widgets."""
    return get_source_of_funds_options(include_empty=True, return_codes=False)

def get_industry_select():
    """Backward compatibility: Get Industry options for select widgets."""
    return get_industry_options(include_empty=True, return_codes=False)


# ===== UTILITY FUNCTIONS =====

def get_controlled_list_manager() -> ControlledListManager:
    """Get the global controlled list manager instance."""
    return _controlled_list_manager

def resolve_codes_to_labels(list_name: str, codes: List[str]) -> List[str]:
    """Convert list of codes to list of labels."""
    if not codes:
        return []
    
    mapping = _controlled_list_manager.get_list_mapping(list_name)
    return [mapping.get(code, code) for code in codes]

def resolve_labels_to_codes(list_name: str, labels: List[str]) -> List[str]:
    """Convert list of labels to list of codes."""
    if not labels:
        return []
    
    mapping = _controlled_list_manager.get_list_mapping(list_name)
    reverse_mapping = {v: k for k, v in mapping.items()}
    return [reverse_mapping.get(label, label) for label in labels]


# ===== VALIDATION FUNCTIONS =====

def validate_controlled_list_value(list_name: str, value: str, is_code: bool = False) -> bool:
    """Validate that a value exists in a controlled list."""
    if not value:  # Empty values are often valid
        return True
        
    if is_code:
        mapping = _controlled_list_manager.get_list_mapping(list_name)
        return value in mapping
    else:
        options = _controlled_list_manager.get_list_options(list_name, include_empty=True, return_codes=False)
        return value in options

def validate_controlled_list_values(list_name: str, values: List[str], is_code: bool = False) -> bool:
    """Validate that all values exist in a controlled list."""
    return all(validate_controlled_list_value(list_name, value, is_code) for value in values)


if __name__ == "__main__":
    # Test the enhanced controlled lists
    print("=== Enhanced Controlled Lists Test ===")
    
    print("\nSource of Funds (first 5):")
    sof = get_source_of_funds_options()[:5]
    for item in sof:
        print(f"  {item}")
    
    print("\nEntity Types:")
    entities = get_entity_types()
    for item in entities:
        print(f"  {item}")
    
    print("\nCountries (first 10):")
    countries = get_countries()[:10]
    for item in countries:
        print(f"  {item}")
    
    print("\nCode/Label Resolution Test:")
    print(f"COMPANY -> {_controlled_list_manager.get_label_for_code('entity_types', 'COMPANY')}")
    print(f"Company -> {_controlled_list_manager.get_code_for_label('entity_types', 'Company')}")
