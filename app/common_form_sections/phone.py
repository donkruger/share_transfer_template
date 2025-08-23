from __future__ import annotations
import re
from typing import Any, Dict, List, Tuple
import streamlit as st

from app.common_form_sections.base import SectionComponent
from app.utils import inst_key
from app.utils import persist_text_input

def _digits_only(s: str) -> str:
    return re.sub(r'\D', '', s or "")

def _phone_ok(dial: str, number: str) -> bool:
    dial = (dial or "").strip()
    num_digits = _digits_only(number)
    if dial == "+27":
        return len(num_digits) == 9 and not num_digits.startswith("0")
    return 6 <= len(num_digits) <= 15

class PhoneComponent(SectionComponent):
    """Reusable phone section."""

    def render(self, *, ns: str, instance_id: str, **config) -> None:
        title = config.get("title", "Contact Number")
        st.subheader(title)
        
        c1, c2 = st.columns([1,2])
        with c1:
            persist_text_input("Dialing Code", inst_key(ns, instance_id, "code"), help="e.g., +27")
        with c2:
            label = "Phone Number (must be 9 digits, no leading 0)" if st.session_state.get(inst_key(ns, instance_id, "code")) == "+27" else "Phone Number (digits only)"
            persist_text_input(label, inst_key(ns, instance_id, "number"))

    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        # Check if development mode is enabled - if so, skip all validation
        try:
            from app.utils import is_dev_mode
            if is_dev_mode():
                return []  # Return empty list (no errors) when dev mode is enabled
        except ImportError:
            pass  # If utils import fails, continue with normal validation
        
        errs: List[str] = []
        dial = st.session_state.get(inst_key(ns, instance_id, "code"), "")
        num = st.session_state.get(inst_key(ns, instance_id, "number"), "")
        
        if not dial: errs.append("[Phone] Dialing Code is required.")
        if not num: errs.append("[Phone] Phone Number is required.")
        if dial and num and not _phone_ok(dial, num):
            errs.append("[Phone] Phone Number is invalid for the specified dialing code.")
        
        return errs

    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        payload = {
            "Dialing Code": st.session_state.get(inst_key(ns, instance_id, "code"), ""),
            "Number": st.session_state.get(inst_key(ns, instance_id, "number"), "")
        }
        return payload, []

# Register
# Component will be registered in __init__.py to avoid circular imports
