"""
Juristic Entities Component
Implements the Entity Roles - Entity Fields Spec for capturing juristic entities.
"""
import streamlit as st
from typing import List, Dict, Any, Tuple

from app.common_form_sections.base import SectionComponent
from app.utils import inst_key
from app.utils import persist_text_input, persist_selectbox, persist_number_input
from app.controlled_lists_enhanced import get_entity_types, get_countries


class JuristicEntitiesComponent(SectionComponent):
    """
    Component for capturing juristic entities according to Entity Roles - Entity Fields Spec.
    
    Required fields per spec:
    1. Entity Type (from controlled lists)
    2. Entity Name (registered name)
    3. Entity Registration Number (if applicable)
    4. Country of Registration (if registered)
    """

    def render(self, *, ns: str, instance_id: str, **config):
        title = config.get("title", "Related Juristic Entities")
        role_label = config.get("role_label", "Entity")
        
        st.subheader(title)
        count_key = inst_key(ns, instance_id, "count")
        n = persist_number_input(f"Number of {role_label.lower()}s", count_key, min_value=0, step=1)

        for i in range(st.session_state.get(count_key, 0)):
            with st.expander(f"{role_label} #{i+1}", expanded=False):
                
                # 1. Entity Type (Required)
                persist_selectbox("Entity Type",
                    inst_key(ns, instance_id, f"entity_type_{i}"),
                    options=get_entity_types(include_empty=True, return_codes=False),
                    help="Select the type of juristic entity")
                
                # 2. Entity Name (Required)
                persist_text_input("Entity Name",
                    inst_key(ns, instance_id, f"entity_name_{i}"),
                    help="Registered name of the entity")
                
                # 3. Entity Registration Number (Conditional)
                registration_number = persist_text_input("Entity Registration Number",
                    inst_key(ns, instance_id, f"registration_number_{i}"),
                    help="Formal registration number if applicable")
                
                # 4. Country of Registration (Required if registration number provided)
                if registration_number:
                    persist_selectbox("Country of Registration",
                        inst_key(ns, instance_id, f"country_of_registration_{i}"),
                        options=get_countries(include_empty=True, return_codes=False),
                        help="Required when registration number is provided")
                
                # Role-specific additional fields
                self._render_role_specific_fields(ns, instance_id, i, config)

    def _render_role_specific_fields(self, ns: str, instance_id: str, i: int, config: dict):
        """Render additional fields based on the role context."""
        role_label = config.get("role_label", "Entity")
        
        # Percentage ownership for Shareholders and Partners
        if role_label.lower() in ["shareholder", "partner"]:
            field_name = "Percentage Shareholding" if role_label.lower() == "shareholder" else "Partner Interest"
            persist_number_input(f"{field_name} (%)",
                inst_key(ns, instance_id, f"percentage_{i}"),
                min_value=0.0, max_value=100.0, step=0.01,
                help=f"Ownership percentage (0-100%)")
        
        # Executive Control for Directors and Partners
        if role_label.lower() in ["director", "partner"]:
            persist_selectbox("Executive Control",
                inst_key(ns, instance_id, f"executive_control_{i}"),
                options=["", "Yes", "No"],
                help="Does this entity exercise executive control?")

    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        errs: List[str] = []
        role_label = config.get("role_label", "Entity")
        min_count = int(config.get("min_count", 0))
        
        count_key = inst_key(ns, instance_id, "count")
        count = st.session_state.get(count_key, 0)
        
        # Check minimum count
        if count < min_count:
            errs.append(f"{role_label}s: At least {min_count} required.")
        
        # Validate individual entity records
        for i in range(count):
            prefix = f"{role_label} #{i+1}"
            
            # Required fields validation
            entity_type = st.session_state.get(inst_key(ns, instance_id, f"entity_type_{i}"), "").strip()
            entity_name = st.session_state.get(inst_key(ns, instance_id, f"entity_name_{i}"), "").strip()
            registration_number = st.session_state.get(inst_key(ns, instance_id, f"registration_number_{i}"), "").strip()
            country_of_registration = st.session_state.get(inst_key(ns, instance_id, f"country_of_registration_{i}"), "").strip()
            
            if not entity_type:
                errs.append(f"{prefix}: Entity Type is required.")
            if not entity_name:
                errs.append(f"{prefix}: Entity Name is required.")
            
            # Conditional validation: Country required if registration number provided
            if registration_number and not country_of_registration:
                errs.append(f"{prefix}: Country of Registration is required when Registration Number is provided.")
            
            # Role-specific validations
            self._validate_role_specific_fields(errs, ns, instance_id, i, prefix, config)
        
        return errs

    def _validate_role_specific_fields(self, errs: List[str], ns: str, instance_id: str, i: int, prefix: str, config: dict):
        """Validate role-specific fields."""
        role_label = config.get("role_label", "Entity")
        
        # Validate percentage fields
        if role_label.lower() in ["shareholder", "partner"]:
            percentage = st.session_state.get(inst_key(ns, instance_id, f"percentage_{i}"), None)
            if percentage is None or percentage < 0 or percentage > 100:
                field_name = "Percentage Shareholding" if role_label.lower() == "shareholder" else "Partner Interest"
                errs.append(f"{prefix}: {field_name} must be between 0% and 100%.")
        
        # Validate executive control
        if role_label.lower() in ["director", "partner"]:
            executive_control = st.session_state.get(inst_key(ns, instance_id, f"executive_control_{i}"), "").strip()
            if not executive_control:
                errs.append(f"{prefix}: Executive Control selection is required.")

    def serialize_answers(self, *, ns: str, instance_id: str, **config) -> dict:
        """Serialize juristic entity data according to Entity Roles - Entity Fields Spec."""
        role_label = config.get("role_label", "Entity")
        count_key = inst_key(ns, instance_id, "count")
        count = st.session_state.get(count_key, 0)
        
        entities = []
        for i in range(count):
            entity_data = {
                "entity_type": st.session_state.get(inst_key(ns, instance_id, f"entity_type_{i}"), "").strip(),
                "entity_name": st.session_state.get(inst_key(ns, instance_id, f"entity_name_{i}"), "").strip(),
                "entity_registration_number": st.session_state.get(inst_key(ns, instance_id, f"registration_number_{i}"), "").strip() or None,
                "country_of_registration": st.session_state.get(inst_key(ns, instance_id, f"country_of_registration_{i}"), "").strip() or None
            }
            
            # Add role-specific fields
            if role_label.lower() in ["shareholder", "partner"]:
                entity_data["percentage"] = st.session_state.get(inst_key(ns, instance_id, f"percentage_{i}"), 0.0)
            
            if role_label.lower() in ["director", "partner"]:
                entity_data["executive_control"] = st.session_state.get(inst_key(ns, instance_id, f"executive_control_{i}"), "")
            
            entities.append(entity_data)
        
        return {f"{role_label.lower()}s": entities}

    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        """
        Serialize juristic entity data for email/PDF generation.
        Returns (payload_dict, uploads_list) per SectionComponent interface.
        """
        role_label = config.get("role_label", "Entity")
        count_key = inst_key(ns, instance_id, "count")
        count = st.session_state.get(count_key, 0)
        
        entities = []
        uploads = []  # Juristic entities typically don't have file uploads
        
        for i in range(count):
            entity_data = {
                "Entity Type": st.session_state.get(inst_key(ns, instance_id, f"entity_type_{i}"), ""),
                "Entity Name": st.session_state.get(inst_key(ns, instance_id, f"entity_name_{i}"), ""),
                "Registration Number": st.session_state.get(inst_key(ns, instance_id, f"registration_number_{i}"), "") or "N/A",
                "Country of Registration": st.session_state.get(inst_key(ns, instance_id, f"country_of_registration_{i}"), "") or "N/A"
            }
            
            # Add role-specific fields for display
            role_lower = role_label.lower()
            if role_lower in ["shareholder", "partner"]:
                field_name = "Percentage Shareholding" if role_lower == "shareholder" else "Partner Interest"
                entity_data[field_name] = f"{st.session_state.get(inst_key(ns, instance_id, f'percentage_{i}'), 0.0)}%"
            
            if role_lower in ["director", "partner"]:
                entity_data["Executive Control"] = st.session_state.get(inst_key(ns, instance_id, f"executive_control_{i}"), "Not specified")
            
            entities.append(entity_data)
        
        payload = {"Count": count, "Records": entities}
        return payload, uploads


# Component will be registered in __init__.py to avoid circular imports
