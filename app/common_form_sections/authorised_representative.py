# app/common_form_sections/authorised_representative.py

from __future__ import annotations
import datetime
import re
from typing import Any, Dict, List, Tuple
import streamlit as st

from app.common_form_sections.base import SectionComponent
from app.common_form_sections import register_component
from app.utils import inst_key
from app.utils import (
    persist_text_input, persist_selectbox, persist_date_input
)
from app.controlled_lists import (
    get_title_options, get_gender_options, get_marital_status_options, get_countries
)

def _digits_only(s: str) -> str:
    """Extract only digits from string."""
    return re.sub(r"\D", "", s or "")

def _luhn_ok(n: str) -> bool:
    """Luhn algorithm check for SA ID validation."""
    n = _digits_only(n)
    total, alt = 0, False
    for d in n[::-1]:
        d = int(d)
        if alt:
            d *= 2
            if d > 9: 
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0

def _valid_sa_id(n: str) -> bool:
    """Validate SA ID Number: 13 digits + Luhn check."""
    n = _digits_only(n)
    return len(n) == 13 and _luhn_ok(n)

def _is_future_date(d: datetime.date | None) -> bool:
    """Check if date is in the future."""
    return bool(d and d > datetime.date.today())

def _is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    email = email.strip()
    if not email:
        return False
    # Basic regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

class AuthorisedRepresentativeComponent(SectionComponent):
    """
    Component for capturing Authorised Representative details.
    
    The Authorised Representative is the individual completing the form 
    on behalf of the entity.
    
    Config (kwargs):
      - title: str = "Authorised Representative" (section heading)
    """

    def render(self, *, ns: str, instance_id: str, **config) -> None:
        title = config.get("title", "Authorised Representative")
        
        st.subheader(title)
        st.caption("The individual completing this form on behalf of the entity.")
        
        # Personal Details Section
        st.markdown("**Personal Details**")
        col1, col2 = st.columns(2)
        
        with col1:
            persist_selectbox("Title", 
                inst_key(ns, instance_id, "title"), 
                options=get_title_options())
            
            persist_text_input("First Name", 
                inst_key(ns, instance_id, "first_name"))
                
            persist_selectbox("Gender", 
                inst_key(ns, instance_id, "gender"), 
                options=get_gender_options())
                
            persist_selectbox("Marital Status", 
                inst_key(ns, instance_id, "marital_status"), 
                options=get_marital_status_options())
        
        with col2:
            persist_text_input("Last Name", 
                inst_key(ns, instance_id, "last_name"))
                
            persist_date_input("Date of Birth", 
                inst_key(ns, instance_id, "date_of_birth"),
                help="Format: YYYY/MM/DD",
                min_value=datetime.date(1900, 1, 1),  # Reasonable minimum birth year
                max_value=datetime.date.today() - datetime.timedelta(days=365*18))  # Minimum 18 years old
        
        # Identification Section
        st.markdown("**Identification**")
        
        id_type = persist_selectbox("Identification Type",
            inst_key(ns, instance_id, "id_type"),
            options=["", "SA ID Number", "Foreign ID Number", "Foreign Passport Number"])
        
        if id_type == "SA ID Number":
            persist_text_input("SA ID Number", 
                inst_key(ns, instance_id, "sa_id"),
                help="13 digits; Luhn validation applied")
                
        elif id_type == "Foreign ID Number":
            persist_text_input("Foreign ID Number", 
                inst_key(ns, instance_id, "foreign_id"))
                
        elif id_type == "Foreign Passport Number":
            col1, col2 = st.columns(2)
            with col1:
                persist_text_input("Passport Number", 
                    inst_key(ns, instance_id, "passport_number"))
                    
            with col2:
                persist_selectbox("Passport Issue Country",
                    inst_key(ns, instance_id, "passport_country"),
                    options=get_countries())
                    
            persist_date_input("Passport Expiry Date",
                inst_key(ns, instance_id, "passport_expiry"),
                min_value=datetime.date.today() + datetime.timedelta(days=1),
                help="Must be a future date")
        
        # Contact Information Section
        st.markdown("**Contact Information**")
        col1, col2 = st.columns(2)
        
        with col1:
            persist_text_input("Email Address", 
                inst_key(ns, instance_id, "email"),
                help="Valid email format required")
                
            persist_selectbox("Citizenship", 
                inst_key(ns, instance_id, "citizenship"), 
                options=get_countries())
        
        with col2:
            persist_text_input("Cell Phone Number", 
                inst_key(ns, instance_id, "cell_phone"),
                help="Include country code (e.g., +27)")
                
            persist_selectbox("Country of Residence", 
                inst_key(ns, instance_id, "country_of_residence"), 
                options=get_countries())
        
        # Address Section
        st.markdown("**Address**")
        
        col1, col2 = st.columns(2)
        with col1:
            persist_text_input("Unit Number", 
                inst_key(ns, instance_id, "unit_number"),
                help="Optional")
            persist_text_input("Street Number", 
                inst_key(ns, instance_id, "street_number"))
                
        with col2:
            persist_text_input("Complex Name", 
                inst_key(ns, instance_id, "complex_name"),
                help="Optional")
            persist_text_input("Street Name", 
                inst_key(ns, instance_id, "street_name"))
        
        col1, col2 = st.columns(2)
        with col1:
            persist_text_input("Suburb", 
                inst_key(ns, instance_id, "suburb"))
            persist_text_input("Code", 
                inst_key(ns, instance_id, "postal_code"))
                
        with col2:
            persist_text_input("City", 
                inst_key(ns, instance_id, "city"))
            persist_selectbox("Province", 
                inst_key(ns, instance_id, "province"), 
                options=["", "Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", 
                        "Limpopo", "Mpumalanga", "Northern Cape", "North West", "Western Cape"])
        
        persist_selectbox("Country", 
            inst_key(ns, instance_id, "address_country"), 
            options=get_countries())

    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        errs: List[str] = []
        prefix = "[Authorised Representative]"
        
        # Required personal details
        if not (st.session_state.get(inst_key(ns, instance_id, "title")) or "").strip():
            errs.append(f"{prefix} Title is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "first_name")) or "").strip():
            errs.append(f"{prefix} First Name is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "last_name")) or "").strip():
            errs.append(f"{prefix} Last Name is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "gender")) or "").strip():
            errs.append(f"{prefix} Gender is required.")
            
        date_of_birth = st.session_state.get(inst_key(ns, instance_id, "date_of_birth"))
        if not date_of_birth:
            errs.append(f"{prefix} Date of Birth is required.")
        elif date_of_birth >= datetime.date.today() - datetime.timedelta(days=365*18):
            errs.append(f"{prefix} Date of Birth indicates person must be at least 18 years old.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "marital_status")) or "").strip():
            errs.append(f"{prefix} Marital Status is required.")
        
        # Identification validation
        id_type = st.session_state.get(inst_key(ns, instance_id, "id_type"), "")
        if not id_type:
            errs.append(f"{prefix} Identification Type is required.")
        elif id_type == "SA ID Number":
            sa_id = st.session_state.get(inst_key(ns, instance_id, "sa_id"), "")
            if not _valid_sa_id(sa_id):
                errs.append(f"{prefix} SA ID Number is invalid (must be 13 digits with valid Luhn check).")
        elif id_type == "Foreign ID Number":
            foreign_id = st.session_state.get(inst_key(ns, instance_id, "foreign_id"), "")
            if not foreign_id.strip():
                errs.append(f"{prefix} Foreign ID Number is required.")
        elif id_type == "Foreign Passport Number":
            passport_number = st.session_state.get(inst_key(ns, instance_id, "passport_number"), "")
            passport_country = st.session_state.get(inst_key(ns, instance_id, "passport_country"), "")
            passport_expiry = st.session_state.get(inst_key(ns, instance_id, "passport_expiry"))
            
            if not passport_number.strip():
                errs.append(f"{prefix} Passport Number is required.")
            if not passport_country.strip():
                errs.append(f"{prefix} Passport Issue Country is required.")
            if not passport_expiry or not _is_future_date(passport_expiry):
                errs.append(f"{prefix} Passport Expiry Date must be a future date.")
        
        # Contact information validation
        email = st.session_state.get(inst_key(ns, instance_id, "email"), "")
        if not _is_valid_email(email):
            errs.append(f"{prefix} Valid Email Address is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "citizenship")) or "").strip():
            errs.append(f"{prefix} Citizenship is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "country_of_residence")) or "").strip():
            errs.append(f"{prefix} Country of Residence is required.")
            
        cell_phone = st.session_state.get(inst_key(ns, instance_id, "cell_phone"), "")
        if not cell_phone.strip():
            errs.append(f"{prefix} Cell Phone Number is required.")
        
        # Address validation
        if not (st.session_state.get(inst_key(ns, instance_id, "street_number")) or "").strip():
            errs.append(f"{prefix} Street Number is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "street_name")) or "").strip():
            errs.append(f"{prefix} Street Name is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "suburb")) or "").strip():
            errs.append(f"{prefix} Suburb is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "city")) or "").strip():
            errs.append(f"{prefix} City is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "postal_code")) or "").strip():
            errs.append(f"{prefix} Code is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "address_country")) or "").strip():
            errs.append(f"{prefix} Country is required.")
        
        return errs

    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        # Collect all authorised representative data
        data = {
            "Title": st.session_state.get(inst_key(ns, instance_id, "title"), ""),
            "First Name": st.session_state.get(inst_key(ns, instance_id, "first_name"), ""),
            "Last Name": st.session_state.get(inst_key(ns, instance_id, "last_name"), ""),
            "Gender": st.session_state.get(inst_key(ns, instance_id, "gender"), ""),
            "Date of Birth": st.session_state.get(inst_key(ns, instance_id, "date_of_birth"), ""),
            "Marital Status": st.session_state.get(inst_key(ns, instance_id, "marital_status"), ""),
            
            "Identification Type": st.session_state.get(inst_key(ns, instance_id, "id_type"), ""),
            "SA ID": st.session_state.get(inst_key(ns, instance_id, "sa_id"), ""),
            "Foreign ID": st.session_state.get(inst_key(ns, instance_id, "foreign_id"), ""),
            "Passport Number": st.session_state.get(inst_key(ns, instance_id, "passport_number"), ""),
            "Passport Country": st.session_state.get(inst_key(ns, instance_id, "passport_country"), ""),
            "Passport Expiry": st.session_state.get(inst_key(ns, instance_id, "passport_expiry"), ""),
            
            "Email": st.session_state.get(inst_key(ns, instance_id, "email"), ""),
            "Citizenship": st.session_state.get(inst_key(ns, instance_id, "citizenship"), ""),
            "Country of Residence": st.session_state.get(inst_key(ns, instance_id, "country_of_residence"), ""),
            "Cell Phone": st.session_state.get(inst_key(ns, instance_id, "cell_phone"), ""),
            
            "Unit Number": st.session_state.get(inst_key(ns, instance_id, "unit_number"), ""),
            "Complex Name": st.session_state.get(inst_key(ns, instance_id, "complex_name"), ""),
            "Street Number": st.session_state.get(inst_key(ns, instance_id, "street_number"), ""),
            "Street Name": st.session_state.get(inst_key(ns, instance_id, "street_name"), ""),
            "Suburb": st.session_state.get(inst_key(ns, instance_id, "suburb"), ""),
            "City": st.session_state.get(inst_key(ns, instance_id, "city"), ""),
            "Code": st.session_state.get(inst_key(ns, instance_id, "postal_code"), ""),
            "Province": st.session_state.get(inst_key(ns, instance_id, "province"), ""),
            "Country": st.session_state.get(inst_key(ns, instance_id, "address_country"), ""),
        }
        
        # Format date of birth if present
        date_of_birth = data["Date of Birth"]
        if isinstance(date_of_birth, datetime.date):
            data["Date of Birth"] = date_of_birth.strftime("%Y/%m/%d")
            
        # Format passport expiry if present
        passport_expiry = data["Passport Expiry"]
        if isinstance(passport_expiry, datetime.date):
            data["Passport Expiry"] = passport_expiry.strftime("%Y/%m/%d")
        
        # No file uploads for this component
        uploads = []
        
        return data, uploads

# Register the component
register_component("authorised_representative", AuthorisedRepresentativeComponent())
