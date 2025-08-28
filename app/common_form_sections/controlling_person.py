"""
Controlling Person Component for FATCA/CRS Compliance

This component captures controlling person information specifically for FATCA and CRS 
requirements, with focused fields rather than the broader natural_persons component.
"""

from __future__ import annotations
import datetime, re
from typing import Any, Dict, List, Tuple
import streamlit as st

from app.common_form_sections.base import SectionComponent
from app.utils import inst_key, persist_text_input, persist_selectbox, persist_number_input, persist_date_input
from app.controlled_lists_enhanced import get_countries, get_tin_options_with_descriptions, get_member_role_options





class ControllingPersonComponent(SectionComponent):
    """
    Component for capturing controlling person information for FATCA/CRS compliance.
    
    This component focuses on the specific fields required for controlling persons
    in FATCA/CRS contexts, rather than using the broader natural_persons component.
    
    Config (kwargs):
      - title: str = "Controlling Person Information"
      - role_label: str = "Controlling Person"
      - min_count: int = 1
      - help_text: str = Optional help text
    """

    def render(self, *, ns: str, instance_id: str, **config) -> None:
        title = config.get("title", "Controlling Person Information") 
        role_label = config.get("role_label", "Controlling Person")
        help_text = config.get("help_text", "")
        
        st.subheader(title)
        if help_text:
            st.info(help_text)
        
        count_key = inst_key(ns, instance_id, "count")
        n = persist_number_input(f"Number of {role_label.lower()}s", count_key, min_value=0, step=1)

        for i in range(st.session_state.get(count_key, 0)):
            with st.expander(f"{role_label} #{i+1}", expanded=False):
                # Personal identification
                col1, col2 = st.columns(2)
                with col1:
                    persist_text_input("First Name", 
                        inst_key(ns, instance_id, f"first_name_{i}"))
                    persist_text_input("Last Name", 
                        inst_key(ns, instance_id, f"last_name_{i}"))
                
                with col2:
                    persist_date_input("Date of Birth", 
                        inst_key(ns, instance_id, f"date_of_birth_{i}"),
                        help="Format: YYYY/MM/DD",
                        min_value=datetime.date(1900, 1, 1),
                        max_value=datetime.date.today() - datetime.timedelta(days=365*18))
                    
                    persist_selectbox("Country of Birth",
                        inst_key(ns, instance_id, f"birth_country_{i}"),
                        options=get_countries(include_empty=True, return_codes=False))

                # Role and Tax Residence (new required fields)
                col1, col2 = st.columns(2)
                with col1:
                    persist_selectbox("Role/Designation",
                        inst_key(ns, instance_id, f"member_role_{i}"),
                        options=get_member_role_options(include_empty=True, return_codes=False),
                        help="Select the role/designation of this controlling person")
                        
                with col2:
                    persist_selectbox("Country of Tax Residence",
                        inst_key(ns, instance_id, f"tax_residence_country_{i}"),
                        options=get_countries(include_empty=True, return_codes=False))



                # TIN Information (specific to controlling persons)
                st.markdown("**Tax Identification**")
                
                # Get the mapping of codes to their descriptive labels
                tin_options = get_tin_options_with_descriptions()
                tin_codes = ["HAS_TIN", "NO_TIN_PROVIDED", "UNABLE_TO_OBTAIN"]
                
                tin_option = persist_selectbox("TIN Option",
                    inst_key(ns, instance_id, f"tin_option_{i}"),
                    options=[""] + tin_codes,
                    format_func=lambda code: tin_options[tin_codes.index(code)] if code in tin_codes else code,
                    help="Select the appropriate Tax Identification Number option")

                if tin_option == "HAS_TIN":
                    persist_text_input("Controlling Person TIN",
                        inst_key(ns, instance_id, f"controlling_person_tin_{i}"),
                        help="Enter the Tax Identification Number for this controlling person")

                # Physical Address (required)
                st.markdown("**Physical Address**")
                
                # Street details
                col1, col2 = st.columns(2)
                with col1:
                    persist_text_input("Street Number",
                        inst_key(ns, instance_id, f"street_number_{i}"))
                    persist_text_input("Unit Number",
                        inst_key(ns, instance_id, f"unit_number_{i}"))
                        
                with col2:
                    persist_text_input("Complex Name",
                        inst_key(ns, instance_id, f"complex_name_{i}"))
                    persist_text_input("Street Name",
                        inst_key(ns, instance_id, f"street_name_{i}"))
                
                # City and regional details
                col1, col2 = st.columns(2)
                with col1:
                    persist_text_input("Suburb",
                        inst_key(ns, instance_id, f"suburb_{i}"))
                    persist_text_input("City",
                        inst_key(ns, instance_id, f"city_{i}"))
                        
                with col2:
                    persist_text_input("Province/State",
                        inst_key(ns, instance_id, f"province_{i}"))
                    persist_text_input("Postal Code",
                        inst_key(ns, instance_id, f"postal_code_{i}"))
                
                # Address country
                persist_selectbox("Address Country",
                    inst_key(ns, instance_id, f"address_country_{i}"),
                    options=get_countries(include_empty=True, return_codes=False))

                # Add separator between people
                if i < st.session_state.get(count_key, 0) - 1:
                    st.markdown("---")

    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        """Validate controlling person data."""
        # Check if development mode is enabled - if so, skip all validation
        try:
            from app.utils import is_dev_mode
            if is_dev_mode():
                return []
        except ImportError:
            pass  # Development mode not available, proceed with normal validation
        
        errors: List[str] = []
        role_label = config.get("role_label", "Controlling Person")
        min_count = int(config.get("min_count", 1))

        n = st.session_state.get(inst_key(ns, instance_id, "count"), 0)
        if n < min_count:
            errors.append(f"[{role_label}s] At least {min_count} entr{'y' if min_count==1 else 'ies'} required.")

        for i in range(n):
            prefix = f"[{role_label} #{i+1}]"
            
            # Required personal information
            first_name = (st.session_state.get(inst_key(ns, instance_id, f"first_name_{i}")) or "").strip()
            if not first_name:
                errors.append(f"{prefix} First Name is required.")
            
            last_name = (st.session_state.get(inst_key(ns, instance_id, f"last_name_{i}")) or "").strip()
            if not last_name:
                errors.append(f"{prefix} Last Name is required.")
            
            # Date of birth validation
            dob = st.session_state.get(inst_key(ns, instance_id, f"date_of_birth_{i}"))
            if not dob:
                errors.append(f"{prefix} Date of Birth is required.")
            elif isinstance(dob, datetime.date):
                # Check minimum age (18 years)
                min_date = datetime.date.today() - datetime.timedelta(days=365*18)
                if dob > min_date:
                    errors.append(f"{prefix} Must be at least 18 years old.")
            
            # Country of birth
            birth_country = (st.session_state.get(inst_key(ns, instance_id, f"birth_country_{i}")) or "").strip()
            if not birth_country:
                errors.append(f"{prefix} Country of Birth is required.")
            
            # Role/Designation
            member_role = (st.session_state.get(inst_key(ns, instance_id, f"member_role_{i}")) or "").strip()
            if not member_role:
                errors.append(f"{prefix} Role/Designation is required.")
            
            # Country of tax residence
            tax_residence_country = (st.session_state.get(inst_key(ns, instance_id, f"tax_residence_country_{i}")) or "").strip()
            if not tax_residence_country:
                errors.append(f"{prefix} Country of Tax Residence is required.")



            # TIN validation
            tin_option = st.session_state.get(inst_key(ns, instance_id, f"tin_option_{i}"), "")
            if not tin_option:
                errors.append(f"{prefix} TIN Option is required.")
            elif tin_option == "HAS_TIN":
                controlling_person_tin = (st.session_state.get(inst_key(ns, instance_id, f"controlling_person_tin_{i}")) or "").strip()
                if not controlling_person_tin:
                    errors.append(f"{prefix} Controlling Person TIN is required when TIN Option is 'Has TIN'.")

            # Physical Address validation (required fields)
            street_number = (st.session_state.get(inst_key(ns, instance_id, f"street_number_{i}")) or "").strip()
            if not street_number:
                errors.append(f"{prefix} Street Number is required.")
            
            street_name = (st.session_state.get(inst_key(ns, instance_id, f"street_name_{i}")) or "").strip()
            if not street_name:
                errors.append(f"{prefix} Street Name is required.")
            
            suburb = (st.session_state.get(inst_key(ns, instance_id, f"suburb_{i}")) or "").strip()
            if not suburb:
                errors.append(f"{prefix} Suburb is required.")
            
            city = (st.session_state.get(inst_key(ns, instance_id, f"city_{i}")) or "").strip()
            if not city:
                errors.append(f"{prefix} City is required.")
            
            postal_code = (st.session_state.get(inst_key(ns, instance_id, f"postal_code_{i}")) or "").strip()
            if not postal_code:
                errors.append(f"{prefix} Postal Code is required.")
            
            address_country = (st.session_state.get(inst_key(ns, instance_id, f"address_country_{i}")) or "").strip()
            if not address_country:
                errors.append(f"{prefix} Address Country is required.")

        return errors

    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        """Serialize controlling person data for export."""
        people: List[Dict[str, Any]] = []
        uploads: List[Any] = []  # No uploads for controlling persons
        n = st.session_state.get(inst_key(ns, instance_id, "count"), 0)

        for i in range(n):
            # Safe date formatting
            dob = st.session_state.get(inst_key(ns, instance_id, f"date_of_birth_{i}"))
            dob_str = ""
            if dob and hasattr(dob, 'strftime'):
                try:
                    dob_str = dob.strftime("%Y/%m/%d")
                except Exception:
                    dob_str = str(dob)

            person_data = {
                # Basic personal information
                "First Name": st.session_state.get(inst_key(ns, instance_id, f"first_name_{i}"), ""),
                "Last Name": st.session_state.get(inst_key(ns, instance_id, f"last_name_{i}"), ""),
                "Date of Birth": dob_str,
                "Country of Birth": st.session_state.get(inst_key(ns, instance_id, f"birth_country_{i}"), ""),
                "Role/Designation": st.session_state.get(inst_key(ns, instance_id, f"member_role_{i}"), ""),
                "Country of Tax Residence": st.session_state.get(inst_key(ns, instance_id, f"tax_residence_country_{i}"), ""),
                

                
                # TIN information
                "TIN Option": st.session_state.get(inst_key(ns, instance_id, f"tin_option_{i}"), ""),
                "Controlling Person TIN": st.session_state.get(inst_key(ns, instance_id, f"controlling_person_tin_{i}"), ""),
                
                # Physical Address
                "Street Number": st.session_state.get(inst_key(ns, instance_id, f"street_number_{i}"), ""),
                "Unit Number": st.session_state.get(inst_key(ns, instance_id, f"unit_number_{i}"), ""),
                "Complex Name": st.session_state.get(inst_key(ns, instance_id, f"complex_name_{i}"), ""),
                "Street Name": st.session_state.get(inst_key(ns, instance_id, f"street_name_{i}"), ""),
                "Suburb": st.session_state.get(inst_key(ns, instance_id, f"suburb_{i}"), ""),
                "City": st.session_state.get(inst_key(ns, instance_id, f"city_{i}"), ""),
                "Province/State": st.session_state.get(inst_key(ns, instance_id, f"province_{i}"), ""),
                "Postal Code": st.session_state.get(inst_key(ns, instance_id, f"postal_code_{i}"), ""),
                "Address Country": st.session_state.get(inst_key(ns, instance_id, f"address_country_{i}"), ""),
            }
            people.append(person_data)

        payload = {"Count": n, "Records": people}
        return payload, uploads


# Register the component
from app.common_form_sections import register_component
register_component("controlling_person", ControllingPersonComponent())
