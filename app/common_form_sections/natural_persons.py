from __future__ import annotations
import datetime, re
from typing import Any, Dict, List, Tuple
import streamlit as st

from app.common_form_sections.base import SectionComponent
from app.common_form_sections import register_component
from app.utils import inst_key
from app.utils import (
    persist_number_input, persist_text_input, persist_selectbox,
    persist_date_input, persist_file_uploader
)
from app.controlled_lists import get_member_role_select

COUNTRIES = ["", "South Africa", "United Kingdom", "United States"]

def _digits_only(s: str) -> str:
    return re.sub(r"\D", "", s or "")

def _luhn_ok(n: str) -> bool:
    n = _digits_only(n)
    total, alt = 0, False
    for d in n[::-1]:
        d = int(d)
        if alt:
            d *= 2
            if d > 9: d -= 9
        total += d
        alt = not alt
    return total % 10 == 0

def _valid_sa_id(n: str) -> bool:
    n = _digits_only(n)
    return len(n) == 13 and _luhn_ok(n)

def _is_future_date(d: datetime.date | None) -> bool:
    return bool(d and d > datetime.date.today())

class NaturalPersonsComponent(SectionComponent):
    """
    Reusable section for capturing a list of natural persons.
    Config (kwargs):
      - title: str = "Related Natural Persons"
      - role_label: str = "Person"    (used in UI headings)
      - min_count: int = 0            (enforce minimum count)
      - show_uploads: bool = True     (toggle ID/PoA uploads)
      - show_member_roles: bool = False (toggle member role selection)
      - allowed_id_types: list[str] = ["SA ID Number", "Foreign ID Number", "Foreign Passport Number"]
    """

    def render(self, *, ns: str, instance_id: str, **config) -> None:
        title = config.get("title", "Related Natural Persons")
        role_label = config.get("role_label", "Person")
        allowed_id_types = config.get("allowed_id_types",
            ["SA ID Number", "Foreign ID Number", "Foreign Passport Number"])

        st.subheader(title)
        count_key = inst_key(ns, instance_id, "count")
        n = persist_number_input(f"Number of {role_label.lower()}s", count_key, min_value=0, step=1)

        for i in range(st.session_state.get(count_key, 0)):
            with st.expander(f"{role_label} #{i+1}", expanded=False):
                persist_text_input("Full Name & Surname", inst_key(ns, instance_id, f"full_{i}"))
                
                # Member role selection (if enabled)
                if config.get("show_member_roles", False):
                    persist_selectbox("Member Role",
                        inst_key(ns, instance_id, f"member_role_{i}"),
                        options=get_member_role_select())

                id_type = persist_selectbox("Identification Type",
                    inst_key(ns, instance_id, f"id_type_{i}"),
                    options=[""] + allowed_id_types)

                if id_type == "SA ID Number":
                    persist_text_input("SA ID Number", inst_key(ns, instance_id, f"sa_id_{i}"),
                                       help="13 digits; Luhn check applies.")
                elif id_type == "Foreign ID Number":
                    persist_text_input("Foreign ID Number", inst_key(ns, instance_id, f"foreign_id_{i}"))
                elif id_type == "Foreign Passport Number":
                    persist_text_input("Passport Number", inst_key(ns, instance_id, f"passport_no_{i}"))
                    persist_selectbox("Passport Issue Country",
                        inst_key(ns, instance_id, f"passport_country_{i}"),
                        options=COUNTRIES)
                    persist_date_input("Passport Expiry (YYYY/MM/DD)",
                        inst_key(ns, instance_id, f"passport_expiry_{i}"),
                        min_value=datetime.date.today() + datetime.timedelta(days=1))

                persist_text_input("Email", inst_key(ns, instance_id, f"email_{i}"))
                persist_text_input("Telephone", inst_key(ns, instance_id, f"tel_{i}"))

                if config.get("show_uploads", True):
                    persist_file_uploader("ID / Passport Document",
                        inst_key(ns, instance_id, f"id_doc_{i}"))
                    persist_file_uploader("Proof of Address",
                        inst_key(ns, instance_id, f"poa_doc_{i}"))

    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        errs: List[str] = []
        role_label = config.get("role_label", "Person")
        min_count = int(config.get("min_count", 0))
        allowed_id_types = config.get("allowed_id_types",
            ["SA ID Number", "Foreign ID Number", "Foreign Passport Number"])

        n = st.session_state.get(inst_key(ns, instance_id, "count"), 0)
        if n < min_count:
            errs.append(f"[{role_label}s] At least {min_count} entr{'y' if min_count==1 else 'ies'} required.")

        for i in range(n):
            prefix = f"[{role_label} #{i+1}]"
            full = (st.session_state.get(inst_key(ns, instance_id, f"full_{i}")) or "").strip()
            if not full:
                errs.append(f"{prefix} Full Name is required.")

            idt = st.session_state.get(inst_key(ns, instance_id, f"id_type_{i}"), "")
            if idt not in [""] + allowed_id_types:
                errs.append(f"{prefix} Invalid ID Type.")
            if not idt:
                errs.append(f"{prefix} Identification Type is required.")
            if idt == "SA ID Number":
                val = st.session_state.get(inst_key(ns, instance_id, f"sa_id_{i}"), "")
                if not _valid_sa_id(val):
                    errs.append(f"{prefix} SA ID Number is invalid.")
            elif idt == "Foreign ID Number":
                if not (st.session_state.get(inst_key(ns, instance_id, f"foreign_id_{i}")) or "").strip():
                    errs.append(f"{prefix} Foreign ID Number is required.")
            elif idt == "Foreign Passport Number":
                if not (st.session_state.get(inst_key(ns, instance_id, f"passport_no_{i}")) or "").strip():
                    errs.append(f"{prefix} Passport Number is required.")
                if not (st.session_state.get(inst_key(ns, instance_id, f"passport_country_{i}")) or "").strip():
                    errs.append(f"{prefix} Passport Issue Country is required.")
                exp = st.session_state.get(inst_key(ns, instance_id, f"passport_expiry_{i}"))
                if not (exp and _is_future_date(exp)):
                    errs.append(f"{prefix} Passport Expiry must be a future date.")
            
            # Member role validation (if enabled)
            if config.get("show_member_roles", False):
                member_role = st.session_state.get(inst_key(ns, instance_id, f"member_role_{i}"), "")
                if not member_role or member_role.strip() == "":
                    errs.append(f"{prefix} Member Role is required.")

        return errs

    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        people: List[Dict[str, Any]] = []
        uploads: List[Any] = []
        n = st.session_state.get(inst_key(ns, instance_id, "count"), 0)

        for i in range(n):
            exp = st.session_state.get(inst_key(ns, instance_id, f"passport_expiry_{i}"))
            person_data = {
                "Full Name": st.session_state.get(inst_key(ns, instance_id, f"full_{i}"), ""),
                "ID Type": st.session_state.get(inst_key(ns, instance_id, f"id_type_{i}"), ""),
                "SA ID": st.session_state.get(inst_key(ns, instance_id, f"sa_id_{i}"), ""),
                "Foreign ID": st.session_state.get(inst_key(ns, instance_id, f"foreign_id_{i}"), ""),
                "Passport No": st.session_state.get(inst_key(ns, instance_id, f"passport_no_{i}"), ""),
                "Passport Country": st.session_state.get(inst_key(ns, instance_id, f"passport_country_{i}"), ""),
                "Passport Expiry": exp.strftime("%Y/%m/%d") if exp else "",
                "Email": st.session_state.get(inst_key(ns, instance_id, f"email_{i}"), ""),
                "Telephone": st.session_state.get(inst_key(ns, instance_id, f"tel_{i}"), ""),
                "ID Doc Uploaded": bool(st.session_state.get(inst_key(ns, instance_id, f"id_doc_{i}"))),
                "PoA Uploaded": bool(st.session_state.get(inst_key(ns, instance_id, f"poa_doc_{i}"))),
            }
            
            # Add member role if enabled
            if config.get("show_member_roles", False):
                person_data["Member Role"] = st.session_state.get(inst_key(ns, instance_id, f"member_role_{i}"), "")
            
            people.append(person_data)
            if config.get("show_uploads", True):
                uploads.extend([
                    st.session_state.get(inst_key(ns, instance_id, f"id_doc_{i}")),
                    st.session_state.get(inst_key(ns, instance_id, f"poa_doc_{i}")),
                ])

        payload = {"Count": n, "Records": people}
        return payload, uploads

# Register
register_component("natural_persons", NaturalPersonsComponent())
